import uuid
import random
from smtplib import SMTPException
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse
# user/views.py
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from backend.models import User, PrivateMessage, Announcement, KnowledgeFile, KnowledgeBase, KnowledgeChunk
from django.db.models import Q
import json
# backend/views.py
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import os
from django.utils.crypto import get_random_string
from backend.utils.parser import extract_text_from_file
from backend.utils.chunker import split_text
from backend.utils.segmenter import auto_clean_and_split, custom_split, split_by_headings
from backend.utils.tree import build_chunk_tree

from backend.utils.vector_store import search_agent_chunks
from backend.utils.qa import ask_llm
from backend.utils.vector_store import add_chunks_to_agent_index

from backend.models import Announcement
from django.utils import timezone
# workflow
from api.core.workflow.executor import Executor
# Redis 客户端配置
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)


def index(request):
    # request.method 请求方式，GET、POST，例如用request.GET.get("key")读取数据
    return HttpResponse("Hello, welcome to our Lingxi Community")


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'msg': '用户名已存在'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'msg': '邮箱已存在'})

        user = User.objects.create(
            username=username,
            password=password,
            email=email
        )
        return JsonResponse({'success': True, 'user_id': user.user_id})
    else:
        return JsonResponse({'success': False, 'msg': '仅支持 POST 请求'})


"""
用户请求发送验证码
"""


@api_view(['POST'])
def send_code(request):
    def generate_code(length=6):
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnopqrstuvwxyz'  # 排除易混淆字符
        return ''.join(random.choices(chars, k=length))

    try:
        email = request.data.get('email')

        # 邮箱格式校验
        validate_email(email)

        # 请求频率控制
        if redis_client.exists(f'code_cooldown_{email}'):
            return JsonResponse({'code': -1, 'message': '请求过于频繁'}, status=429)

        # 3. 生成6位混合验证码
        code = generate_code(6)

        # 4. 存储验证码（覆盖旧值）
        redis_client.setex(f'verification_code_{email}', 300, code)
        redis_client.setex(f'code_cooldown_{email}', 30, '1')  # 冷却期

        # 5. 发送邮件（HTML+文本双版本）
        subject = "灵犀AI社区安全验证码"
        text_content = f"您的验证码是：{code}，5分钟内有效"
        html_content = f"<p>验证码：<strong>{code}</strong></p>"

        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return JsonResponse({'code': 0, 'message': '验证码已发送'})

    except ValidationError:
        return JsonResponse({'code': -1, 'message': '邮箱格式无效'}, status=400)
    except SMTPException as e:
        return JsonResponse({'code': -1, 'message': '邮件服务暂不可用'}, status=503)
    except Exception as e:
        return JsonResponse({'code': -1, 'message': str(e)}, status=500)


'''
用户验证码登录接口
'''


def user_login_by_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', None)
        code = data.get('code', None)
        print(email, code)
        stored_code = redis_client.get(f'verification_code_{email}')
        if not stored_code or stored_code != code:
            return JsonResponse({
                'code': -1,
                'message': '验证码不正确或已过期'
            })

        # 删除Redis中的验证码
        redis_client.delete(f'verification_code_{email}')

        # 尝试获取用户信息
        try:
            user = User.objects.get(email=email)
            user_id = user.user_id
        except User.DoesNotExist:
            # 用户不存在，创建新用户
            username = email.split('@')[0]  # 使用邮箱前缀作为用户名
            user = User.objects.create(
                username=username,
                email=email,
                password='',  # 密码可以稍后设置或留空
            )
            user_id = user.user_id

        # 生成登录token
        token = str(uuid.uuid4())

        # 将token存储到Redis中，设置过期时间为30分钟
        redis_client.setex(f'token_{user_id}', 1800, token)

        # 返回成功响应json
        return JsonResponse({
            'code': 0,
            'message': '登录成功',
            'token': token,
            'id': user_id
        })

    except Exception as e:
        # 捕获异常并返回错误信息
        return JsonResponse({
            'code': -1,
            'message': str(e)
        })


"""
用户密码登录接口
"""


def user_login_by_password(request):
    try:
        data = json.loads(request.body)
        account = data.get('account', None)
        password = data.get('password', None)

        # 获取用户信息
        if '@' in account and '.' in account:
            try:
                user = User.objects.get(email=account)
            except User.DoesNotExist:
                return JsonResponse({
                    'code': -1,
                    'message': '用户不存在'
                })
        else:
            try:
                user = User.objects.get(username=account)
            except User.DoesNotExist:
                return JsonResponse({
                    'code': -1,
                    'message': '用户不存在'
                })

        # 验证密码
        if user.password != password:
            return JsonResponse({
                'code': -1,
                'message': '密码错误'
            })

        # 生成登录token
        token = str(uuid.uuid4())
        user_id = user.user_id

        # 将token存储到Redis中，设置过期时间为30分钟
        redis_client.setex(f'token_{user_id}', 1800, token)

        # 返回成功响应
        return JsonResponse({
            'code': 0,
            'message': '登录成功',
            'token': token,
            'id': user_id
        })

    except Exception as e:
        return JsonResponse({
            'code': -1,
            'message': str(e)
        })


"""
用户修改个人信息接口
"""


def user_update_profile(request):
    try:
        uid = request.POST.get('uid')
        name = request.POST.get('name')
        avatar = request.FILES.get('avatar')  # 从文件中获取头像
        description = request.POST.get('description')
        password = request.POST.get('password')

        if not uid:
            return JsonResponse({"code": -1, "message": "缺少用户ID"})
        if not name:
            return JsonResponse({"code": -1, "message": "昵称不能为空"})

        try:
            user = User.objects.get(user_id=uid)
            user.username = name
            if avatar:
                user.avatar = avatar  # 会自动保存到 MEDIA_ROOT 下的 avatars/
            if description:
                user.description = description
            if password:
                user.password = password
            user.save()

            return JsonResponse({"code": 0, "message": "修改成功"})
        except User.DoesNotExist:
            return JsonResponse({"code": -1, "message": "用户不存在"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": str(e)})


def user_fetch_profile(request):
    uid = request.GET.get('uid')
    if not uid:
        return JsonResponse({"code": -1, "message": "缺少参数 uid"})

    try:
        user = User.objects.get(user_id=uid)

        # 获取相关信息
        data = {
            "name": user.username,
            "account": user.email,
            "avatar": user.avatar.url if hasattr(user, 'avatar') else "",  # 避免字段不存在时报错
            "description": user.description if hasattr(user, 'description') else "",
            "following": user.following_count,
            "followers": user.fans_count,
        }

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "data": data
        })

    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})
    except Exception as e:
        return JsonResponse({"code": -1, "message": str(e)})


AVATAR_DIR = os.path.join(settings.MEDIA_ROOT, 'avatars')
AVATAR_URL_BASE = settings.MEDIA_URL + 'avatars/'

os.makedirs(AVATAR_DIR, exist_ok=True)


@csrf_exempt
def user_update_avatar(request):
    uid = request.POST.get('uid')
    avatar = request.FILES.get('avatar')

    if not uid or not avatar:
        return JsonResponse({"code": -1, "message": "uid 或 avatar 缺失"})

    try:
        user = User.objects.get(user_id=uid)

        # 创建头像保存路径
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)

        # 构造文件名，使用用户id作为文件名
        _, ext = os.path.splitext(avatar.name)
        filename = f"{uid}{ext}"
        filepath = os.path.join(avatar_dir, filename)

        # 删除旧头像（如果存在）
        if os.path.exists(filepath):
            os.remove(filepath)

        # 写入文件
        with open(filepath, 'wb+') as destination:
            for chunk in avatar.chunks():
                destination.write(chunk)

        # 构造 URL（这是 Nginx 公开访问路径）
        avatar_url = f"/media/avatars/{filename}"
        user.avatar_url = avatar_url  # 你需要在 User 模型里加一个 avatar_url 字段
        user.save()

        return JsonResponse({"code": 0, "message": "上传成功", "avatar": avatar_url})
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"上传失败：{str(e)}"})


def user_get_avatar(request):
    uid = request.GET.get('uid')
    if not uid:
        return JsonResponse({"code": -1, "message": "缺少 uid 参数", "avatar": ""})

    try:
        user = User.objects.get(user_id=uid)
        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "avatar": user.avatar_url  # 返回的是 Nginx 可访问的 URL
        })
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在", "avatar": ""})


def user_get_contacts(request):
    try:
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse({"code": -1, "message": "缺少uid参数"})

        try:
            user = User.objects.get(user_id=uid)
        except User.DoesNotExist:
            return JsonResponse({"code": -1, "message": "用户不存在"})

        # 查询与该用户有通信记录的用户（联系人）
        messages = PrivateMessage.objects.filter(Q(sender=user) | Q(receiver=user)) \
            .select_related('sender', 'receiver') \
            .order_by('-send_time')

        latest_msg_map = {}

        for msg in messages:
            contact_user = msg.receiver if msg.sender == user else msg.sender
            cid = contact_user.user_id
            if cid not in latest_msg_map:
                latest_msg_map[cid] = msg  # 第一次
            elif msg.send_time > latest_msg_map[cid].send_time:
                latest_msg_map[cid] = msg  # 更新为更晚的消息

        # 然后再统一生成联系人信息
        contact_dict = {}
        for idx, (cid, msg) in enumerate(latest_msg_map.items(), start=1):
            contact_user = msg.receiver if msg.sender == user else msg.sender
            contact_dict[cid] = {
                "id": idx,
                "name": contact_user.username,
                "avatar": contact_user.avatar.url if contact_user.avatar else "",
                "unread": PrivateMessage.objects.filter(sender=contact_user, receiver=user, is_read=False).count(),
                "lastMessage": {
                    "text": msg.content
                },
                "lastMessageTime": msg.send_time
            }

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "data": list(contact_dict.values())
        })

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"服务器错误: {str(e)}"})


def user_get_messages(request):
    try:
        uid1 = request.GET.get('messagerId1')
        uid2 = request.GET.get('messagerId2')

        if not uid1 or not uid2:
            return JsonResponse({"code": -1, "message": "缺少参数 messagerId1 或 messagerId2"})

        try:
            user1 = User.objects.get(user_id=uid1)
            user2 = User.objects.get(user_id=uid2)
        except User.DoesNotExist:
            return JsonResponse({"code": -1, "message": "用户不存在"})

        # 查询二人之间的所有消息
        messages = PrivateMessage.objects.filter(
            (Q(sender=user1) & Q(receiver=user2)) |
            (Q(sender=user2) & Q(receiver=user1))
        ).select_related('sender').order_by('send_time')  # 正序时间排序

        # 标记对 user1 来说“未读且是 user2 发来的消息”为已读
        PrivateMessage.objects.filter(sender=user2, receiver=user1, is_read=False).update(is_read=True)

        data = []
        for msg in messages:
            data.append({
                "sender": msg.sender.username,
                "avatar": msg.sender.avatar.url if msg.sender.avatar else "",
                "time": msg.send_time,
                "text": msg.content
            })

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "data": data
        })

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"服务器错误: {str(e)}"})


def user_send_message(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        sender_id = data.get("sender")
        receiver_id = data.get("receiver")
        message_text = data.get("message")

        if not sender_id or not receiver_id or not message_text:
            return JsonResponse({"code": -1, "message": "缺少必要字段"})

        try:
            sender = User.objects.get(user_id=sender_id)
            receiver = User.objects.get(user_id=receiver_id)
        except User.DoesNotExist:
            return JsonResponse({"code": -1, "message": "发送方或接收方用户不存在"})

        # 创建消息
        PrivateMessage.objects.create(
            sender=sender,
            receiver=receiver,
            content=message_text,
            send_time=timezone.now(),
            is_read=False
        )

        return JsonResponse({"code": 0, "message": "发送成功"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"发送失败: {str(e)}"})


# Announcement
@api_view(['POST'])
def announcement_add(request):
    """
    添加公告
    请求：POST /anno/add
    """
    # 从请求中获取公告的标题和内容
    title = request.data.get('title')
    content = request.data.get('content')

    # 参数验证：标题和内容是必填字段
    if not title or not content:
        return Response({
            'code': -1,
            'message': 'Title and content are required.',
            'announcements': []
        }, status=status.HTTP_400_BAD_REQUEST)

    # 创建新的公告
    announcement = Announcement.objects.create(
        title=title,
        content=content,
        time=timezone.now()
    )

    # 返回包含新公告的响应
    return Response({
        'code': 0,
        'message': '添加成功',
        'announcements': [{
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'time': announcement.time.isoformat()
        }]
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def announcement_update(request):
    """
    更新公告
    请求：PUT /anno/update
    """
    # 从请求中获取公告的ID、标题和内容
    announcement_id = request.data.get('id')
    title = request.data.get('title')
    content = request.data.get('content')

    # 验证公告是否存在
    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        return Response({
            'code': -1,
            'message': 'Announcement not found.',
            'announcements': []
        }, status=status.HTTP_404_NOT_FOUND)

    # 更新公告字段
    if title:
        announcement.title = title
    if content:
        announcement.content = content

    # 更新修改时间
    announcement.time = timezone.now()
    announcement.save()

    # 返回更新后的公告信息
    return Response({
        'code': 0,
        'message': '更新成功',
        'announcements': [{
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'time': announcement.time.isoformat()
        }]
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def announcement_delete(request):
    """
    删除公告
    请求：DELETE /anno/delete
    """
    # 从请求中获取公告ID
    announcement_id = request.data.get('id')

    # 尝试查找并删除公告
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.delete()
        return Response({
            'code': 0,
            'message': '删除成功',
            'announcements': []
        }, status=status.HTTP_200_OK)
    except Announcement.DoesNotExist:
        return Response({
            'code': -1,
            'message': 'Announcement not found.',
            'announcements': []
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def announcement_list(request):
    """
    获取所有公告
    请求：GET /anno/get
    """
    # 获取所有公告
    announcements = Announcement.objects.all()

    # 如果没有公告，返回空的公告列表
    if not announcements:
        return Response({
            'code': 0,
            'message': '获取成功',
            'announcements': []
        })

    # 构建公告列表数据
    data = [{
        'id': announcement.id,
        'title': announcement.title,
        'content': announcement.content,
        'time': announcement.time.isoformat()
    } for announcement in announcements]

    # 返回公告列表
    return Response({
        'code': 0,
        'message': '获取成功',
        'announcements': data
    })


@api_view(['POST'])
def user_update_password(request):
    data = json.loads(request.body)

    uid = data['uid']
    old_password = data['oldPwd']
    new_password = data['newPwd']

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return Response({
            'code': -1,
            'message': '该用户不存在'
        })

    if user.password != old_password:
        return JsonResponse({
            'code': -1,
            'message': '密码错误'
        })

    user.password = new_password
    user.save()
    return Response({
        'code': 0,
        'message': '更新成功'
    })

@csrf_exempt
def create_kb(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    user_id = request.POST.get('user_id')
    kb_name = request.POST.get('kb_name')
    kb_type = request.POST.get('kb_type', '')
    kb_description = request.POST.get('kb_description', '')

    if not user_id or not kb_name:
        return JsonResponse({"code": -1, "message": "缺少 user_id 或 kb_name 参数"})

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    if KnowledgeBase.objects.filter(kb_name=kb_name, user=user).exists():
        return JsonResponse({"code": 1, "message": "该用户下已存在同名知识库"})

    kb = KnowledgeBase.objects.create(
        user=user,
        kb_name=kb_name,
        kb_type=kb_type,
        kb_description=kb_description,
    )
    return JsonResponse({
        "code": 0,
        "message": "创建成功",
        "kb_id": kb.kb_id,
        "uuid": str(kb.uuid),
    })

ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md']

@csrf_exempt
def upload_kb_file(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    kb_id = request.POST.get('kb_id')
    segment_mode = request.POST.get('segment_mode', 'auto')
    file = request.FILES.get('file')

    if not kb_id or not file:
        return JsonResponse({"code": -1, "message": "缺少 kb_id 或 file"})

    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({"code": -1, "message": "不支持的文件类型"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=request.user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    saved_file = KnowledgeFile.objects.create(
        kb=kb,
        file=file,
        name=file.name,
        segment_mode=segment_mode
    )

    try:
        segment_file_and_save_chunks(saved_file, segment_mode)
    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"上传成功但分段失败: {str(e)}",
            "file_id": saved_file.id
        })

    return JsonResponse({
        "code": 0,
        "message": "上传成功",
        "id": saved_file.id,
        "name": saved_file.name
    })

def segment_file_and_save_chunks(file_obj, segment_mode, max_length=200):
    text = extract_text_from_file(file_obj.file.path)
    kb = file_obj.kb

    KnowledgeChunk.objects.filter(file=file_obj).delete()

    if segment_mode == 'auto':
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            KnowledgeChunk.objects.create(kb=kb, file=file_obj, content=para, order=i)

    elif segment_mode == 'custom':
        words = text.split()
        i = 0
        order = 0
        while i < len(words):
            chunk_text = ' '.join(words[i:i+max_length])
            KnowledgeChunk.objects.create(kb=kb, file=file_obj, content=chunk_text, order=order)
            i += max_length
            order += 1

    elif segment_mode == 'hierarchical':
        lines = text.splitlines()
        current_parent = None
        order = 0
        for line in lines:
            if line.startswith("#"):
                current_parent = KnowledgeChunk.objects.create(kb=kb, file=file_obj, content=line.strip(), order=order)
            elif line.strip():
                KnowledgeChunk.objects.create(kb=kb, file=file_obj, content=line.strip(), order=order, parent=current_parent)
            order += 1
    else:
        raise ValueError("不支持的分段方式")

@csrf_exempt
def get_kb_file_chunks(request):
    file_id = request.GET.get('file_id')
    if not file_id:
        return JsonResponse({"code": -1, "message": "缺少 file_id 参数"})

    try:
        file_obj = KnowledgeFile.objects.get(id=file_id)
    except KnowledgeFile.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识文件不存在"})

    chunks = KnowledgeChunk.objects.filter(file=file_obj).order_by('order')

    if file_obj.segment_mode == 'hierarchical':
        # 构建树形结构
        chunk_dict = {}
        for chunk in chunks:
            chunk_dict[chunk.chunk_id] = {
                "id": chunk.chunk_id,
                "content": chunk.content,
                "order": chunk.order,
                "children": []
            }

        tree = []
        for chunk in chunks:
            if chunk.parent_id:
                chunk_dict[chunk.parent_id]["children"].append(chunk_dict[chunk.chunk_id])
            else:
                tree.append(chunk_dict[chunk.chunk_id])

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "chunks": tree,
            "mode": file_obj.segment_mode
        })

    else:
        # 普通列表结构（auto / custom）
        chunk_list = [{
            "id": chunk.chunk_id,
            "content": chunk.content,
            "order": chunk.order
        } for chunk in chunks]

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "chunks": chunk_list,
            "mode": file_obj.segment_mode
        })


class UploadKnowledgeFileView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, kb_id):
        uploaded_file = request.FILES['file']
        segment_mode = request.data.get('segment_mode', 'auto')
        agent_id = request.data.get('agent_id')

        if not agent_id:
            return Response({'error': '请提供 agent_id'}, status=400)

        try:
            kb = KnowledgeBase.objects.get(pk=kb_id)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': '知识库不存在'}, status=404)

        # 保存文件信息
        file = KnowledgeFile.objects.create(
            kb=kb,
            file=uploaded_file,
            name=uploaded_file.name,
            segment_mode=segment_mode
        )

        abs_path = file.file.path
        text = parse_file(abs_path)

        # 参数读取（仅 custom 模式用）
        max_len = int(request.data.get('max_len', 300))
        overlap = int(request.data.get('overlap', 30))
        clean = request.data.get('clean', 'true') == 'true'

        chunk_objs = []

        if segment_mode == 'auto':
            chunks = auto_clean_and_split(text)
            for i, chunk_text in enumerate(chunks):
                chunk = KnowledgeChunk.objects.create(
                    kb=kb,
                    file=file,
                    content=chunk_text,
                    order=i
                )
                chunk_objs.append(chunk)

        elif segment_mode == 'custom':
            chunks = custom_split(text, max_len=max_len, overlap=overlap, clean=clean)
            for i, chunk_text in enumerate(chunks):
                chunk = KnowledgeChunk.objects.create(
                    kb=kb,
                    file=file,
                    content=chunk_text,
                    order=i
                )
                chunk_objs.append(chunk)

        elif segment_mode == 'hierarchical':
            parts = split_by_headings(text)
            chunk_map = {}

            for i, part in enumerate(parts):
                parent_chunk = chunk_map.get(id(part['parent'])) if part['parent'] else None
                chunk = KnowledgeChunk.objects.create(
                    kb=kb,
                    file=file,
                    content=part['content'],
                    order=i,
                    parent=parent_chunk
                )
                chunk_map[id(part)] = chunk
                chunk_objs.append(chunk)

        else:
            return Response({'error': 'Invalid segment_mode'}, status=400)

        # ✅ 加入 Agent 专属向量索引
        try:
            add_chunks_to_agent_index(agent_id=agent_id, chunks=chunk_objs)
        except Exception as e:
            return Response({'error': f'构建向量索引失败: {str(e)}'}, status=500)

        return Response({
            'file_id': file.id,
            'chunk_count': len(chunk_objs),
            'segment_mode': segment_mode
        })


class ChunkTreeView(APIView):
    def get(self, request, kb_id, file_id):
        try:
            chunks = KnowledgeChunk.objects.filter(
                kb_id=kb_id,
                file_id=file_id
            ).order_by('order')
            tree = build_chunk_tree(chunks)
            return Response(tree)
        except KnowledgeFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


class ChunkListView(APIView):
    def get(self, request, kb_id, file_id):
        mode = request.query_params.get('mode', 'auto')  # 默认为自动
        try:
            chunks = KnowledgeChunk.objects.filter(
                kb_id=kb_id,
                file_id=file_id,
                parent=None if mode != 'hierarchical' else None
            ).order_by('order')

            if mode == 'hierarchical':
                return Response({'error': 'Use /tree/ endpoint for hierarchical'}, status=400)

            chunk_list = [
                {
                    'id': chunk.id,
                    'content': chunk.content,
                    'order': chunk.order
                }
                for chunk in chunks
            ]
            return Response(chunk_list)

        except KnowledgeChunk.DoesNotExist:
            return Response({'error': 'Chunks not found'}, status=404)


class VectorSearchView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Missing query'}, status=400)

        results = search_agent_chunks(query)
        return Response(results)


@api_view(['POST'])
def ask_question(request):
    query = request.data.get("query")
    agent_id = request.data.get("agent_id")

    if not query or not agent_id:
        return Response({"error": "请提供 query 和 agent_id"}, status=400)

    # 检索专属 Agent 的向量库
    related_chunks = search_agent_chunks(agent_id, query)

    try:
        answer = ask_llm(query, related_chunks)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response({
        "question": query,
        "answer": answer,
        "context": related_chunks
    })
def workflow_run(request):
    nodes = request.data.get("nodes", [])
    edges = request.data.get("edges", [])
    user_id = request.user.id
    workflow_id = request.data.get("workflowId")

    executor = Executor(user_id, workflow_id, nodes, edges)
    result = executor.execute()
    return JsonResponse({"result": result})
