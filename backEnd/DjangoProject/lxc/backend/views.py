import uuid
import random

from django.views import View
from openai import OpenAI
import dashscope
from http import HTTPStatus
from smtplib import SMTPException
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse
from django.utils.timezone import localtime
# user/views.py
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from pycparser import parse_file

from api.core.workflow.executor import Executor
from backend.models import User, PrivateMessage, Announcement, KnowledgeFile, KnowledgeBase, KnowledgeChunk, Workflow,Agent,UserInteraction,FollowRelationship,Comment,SensitiveWord
from django.db.models import Q, ExpressionWrapper, F, IntegerField
import base64
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
from .utils.segmenter import auto_clean_and_split, custom_split, split_by_headings
from .utils.tree import build_chunk_tree

from .utils.vector_store import search_agent_chunks
from .utils.qa import ask_llm
from .utils.vector_store import add_chunks_to_agent_index
from .models import Announcement, AgentReport, Administrator
import pandas as pd
import requests

# workflow

# Redis 客户端配置
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)


def index(request):
    # request.method 请求方式，GET、POST，例如用request.GET.get("key")读取数据
    return HttpResponse("Hello, welcome to our Lingxi Community")

def check_user_post_status(user):
    if not user.can_post:
        now = timezone.now()
        if user.post_expire and now >= user.post_expire:
            user.can_post = True
            user.post_expire = None
            user.save()
            return None  # 解封成功，可发布
        else:
            return f"您当前被禁止发布，解封时间为：{user.post_expire.strftime('%Y-%m-%d %H:%M:%S')}"
    return None  # 可发布

def check_user_ban_status(user):
    if user.is_banned:
        now = timezone.now()
        if user.ban_expire and now >= user.ban_expire:
            user.is_banned = False
            user.ban_expire = None
            user.save()
            return None  # 解封成功
        else:
            return f"账号已被封禁，解封时间为：{user.ban_expire.strftime('%Y-%m-%d %H:%M:%S')}"
    return None  # 没有封禁

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

@csrf_exempt
@api_view(['POST'])
def send_code(request):
    def generate_code(length=6):
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnopqrstuvwxyz'
        return ''.join(random.choices(chars, k=length))

    try:
        email = request.data.get('email')

        # 邮箱格式校验
        validate_email(email)

        # 若邮箱已注册，检查封禁状态
        try:
            user = User.objects.get(email=email)
            ban_message = check_user_ban_status(user)
            if ban_message:
                return JsonResponse({
                    'code': -1,
                    'message': ban_message
                }, status=200)
        except User.DoesNotExist:
            pass  # 用户不存在则允许请求验证码以供注册

        # 请求频率控制
        if redis_client.exists(f'code_cooldown_{email}'):
            return JsonResponse({'code': -1, 'message': '请求过于频繁'}, status=429)

        code = generate_code(6)
        redis_client.setex(f'verification_code_{email}', 300, code)
        redis_client.setex(f'code_cooldown_{email}', 30, '1')

        subject = "灵犀AI社区安全验证码"
        text_content = f"您的验证码是：{code}，5分钟内有效"
        html_content = f"<p>验证码：<strong>{code}</strong></p>"

        email_msg = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        return JsonResponse({'code': 0, 'message': '验证码已发送'})

    except ValidationError:
        return JsonResponse({'code': -1, 'message': '邮箱格式无效'}, status=400)
    except SMTPException:
        return JsonResponse({'code': -1, 'message': '邮件服务暂不可用'}, status=503)
    except Exception as e:
        return JsonResponse({'code': -1, 'message': str(e)}, status=500)
'''
用户验证码登录接口
'''
@csrf_exempt
def user_login_by_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', None)
        code = data.get('code', None)

        stored_code = redis_client.get(f'verification_code_{email}')
        if not stored_code or stored_code != code:
            return JsonResponse({
                'code': -1,
                'message': '验证码不正确或已过期'
            })

        redis_client.delete(f'verification_code_{email}')

        is_new_user = False

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = email.split('@')[0]
            default_avatar = '/media/avatars/defaultAvatar.svg'
            user = User.objects.create(
                username=username,
                email=email,
                password='123456',
                avatar_url=default_avatar
            )
            is_new_user = True

        # 检查封禁状态
        ban_message = check_user_ban_status(user)
        if ban_message:
            return JsonResponse({
                'code': -1,
                'message': ban_message
            })

        token = str(uuid.uuid4())
        redis_client.setex(f'token_{user.user_id}', 1800, token)

        return JsonResponse({
            'code': 0,
            'message': '登录成功',
            'token': token,
            'id': user.user_id,
            'is_new_user': is_new_user
        })

    except Exception as e:
        return JsonResponse({
            'code': -1,
            'message': str(e)
        })

"""
用户密码登录接口
"""
@csrf_exempt
def user_login_by_password(request):
    try:
        data = json.loads(request.body)
        account = data.get('account', None)
        password = data.get('password', None)

        if '@' in account and '.' in account:
            try:
                user = User.objects.get(email=account)
            except User.DoesNotExist:
                return JsonResponse({'code': -1, 'message': '用户不存在'})
        else:
            try:
                user = User.objects.get(username=account)
            except User.DoesNotExist:
                return JsonResponse({'code': -1, 'message': '用户不存在'})

        # 检查封禁状态
        ban_message = check_user_ban_status(user)
        if ban_message:
            return JsonResponse({
                'code': -1,
                'message': ban_message
            })

        if user.password != password:
            return JsonResponse({'code': -1, 'message': '密码错误'})

        token = str(uuid.uuid4())
        redis_client.setex(f'token_{user.user_id}', 1800, token)

        return JsonResponse({
            'code': 0,
            'message': '登录成功',
            'token': token,
            'id': user.user_id
        })

    except Exception as e:
        return JsonResponse({'code': -1, 'message': str(e)})


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

@csrf_exempt
def update_basic_info(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        body = json.loads(request.body.decode('utf-8'))
        uid = body.get('uid')
        name = body.get('name')
        description = body.get('description')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or name is None or description is None:
        return JsonResponse({"code": -1, "message": "缺少必要参数"})

    try:
        user = User.objects.get(user_id=uid)
        user.username = name
        user.description = description
        user.save()

        return JsonResponse({"code": 0, "message": "更新成功"})
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"更新失败: {str(e)}"})

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
        for cid, msg in latest_msg_map.items():
            contact_user = msg.receiver if msg.sender == user else msg.sender
            contact_dict[cid] = {
                "id": contact_user.user_id,  # ✅ 使用真实数据库主键
                "name": contact_user.username,
                "avatar": contact_user.avatar_url,
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
                "time": msg.send_time,
                "text": msg.content,
                "avatar": msg.sender.avatar_url,
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
    }, status=status.HTTP_200_OK)


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

    uid = request.POST.get('uid')
    kb_name = request.POST.get('kb_name')
    kb_type = request.POST.get('kb_type', '')
    kb_description = request.POST.get('kb_description', '')
    kb_icon = request.FILES.get('kb_icon')  # 可选图标

    if not uid or not kb_name:
        return JsonResponse({"code": -1, "message": "缺少 uid 或 kb_name 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    if KnowledgeBase.objects.filter(kb_name=kb_name, user=user).exists():
        return JsonResponse({"code": 1, "message": "该用户下已存在同名知识库"})

    # 第一步：创建知识库对象（不含图标）
    kb = KnowledgeBase.objects.create(
        user=user,
        kb_name=kb_name,
        kb_type=kb_type,
        kb_description=kb_description,
    )

    # 第二步：处理图标保存
    if kb_icon:
        ICON_DIR = os.path.join(settings.MEDIA_ROOT, 'kb_icons')
        os.makedirs(ICON_DIR, exist_ok=True)

        _, ext = os.path.splitext(kb_icon.name)
        filename = f"{kb.kb_id}{ext}"
        filepath = os.path.join(ICON_DIR, filename)

        with open(filepath, 'wb+') as destination:
            for chunk in kb_icon.chunks():
                destination.write(chunk)

        kb.icon = f"/media/kb_icons/{filename}"
        kb.save()
    else:
        # 没上传图标，根据 kb_type 使用默认图标（kb_type 英文，大小写不敏感）
        type_to_icon = {
            "text": "Text.svg",
            "table": "Table.svg",
            "picture": "Picture.svg",
        }

        # 防止kb_type异常，同时统一小写处理
        kb_type_cleaned = (kb_type or "").strip().lower()

        default_icon_file = type_to_icon.get(kb_type_cleaned, "Text.svg")

        kb.icon = f"/media/kb_icons/{default_icon_file}"
        kb.save()

    return JsonResponse({
        "code": 0,
        "message": "创建成功",
        "kb_id": kb.kb_id,
        "uuid": str(kb.uuid),
        "icon": kb.icon
    })


ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md']

@csrf_exempt
def upload_kb_file(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    uid = request.POST.get('uid')
    kb_id = request.POST.get('kb_id')
    segment_mode = request.POST.get('segment_mode', 'auto')
    file = request.FILES.get('file')

    if not uid or not kb_id or not file:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 file"})

    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({"code": -1, "message": "不支持的文件类型"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    saved_file = KnowledgeFile.objects.create(
        kb=kb,
        file=file,
        name=file.name,
        segment_mode=segment_mode
    )

    kb.updated_at = timezone.now()
    kb.save()

    try:
        segment_file_and_save_chunks(saved_file, segment_mode)
    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"上传成功但处理失败: {str(e)}"
        })

    return JsonResponse({
        "code": 0,
        "message": "上传成功"
    })

def get_tongyi_embedding(text):
    # 从 settings 中获取 API KEY
    dashscope.api_key = getattr(settings, "DASHSCOPE_API_KEY", None)

    if not dashscope.api_key:
        print("[通义嵌入失败] 未配置 DASHSCOPE_API_KEY")
        return None

    try:
        resp = dashscope.TextEmbedding.call(
            model=dashscope.TextEmbedding.Models.text_embedding_v3,
            input=text,
            dimension=1024,
            output_type="dense&sparse"
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.output["embeddings"][0]["embedding"]  # 取出嵌入向量
        else:
            print(f"[通义嵌入异常返回] {resp}")
            return None
    except Exception as e:
        print(f"[通义嵌入失败] {str(e)}")
        return None

@csrf_exempt
def get_kb_files(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    uid = request.GET.get('uid')
    kb_id = request.GET.get('kb_id')

    if not uid or not kb_id:
        return JsonResponse({"code": -1, "message": "缺少 uid 或 kb_id 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    files = kb.files.all().values('id', 'name')
    file_list = list(files)

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "texts": file_list
    })

def segment_file_and_save_chunks(file_obj, segment_mode, max_length=200):
    text = extract_text_from_file(file_obj.file.path)
    kb = file_obj.kb

    KnowledgeChunk.objects.filter(file=file_obj).delete()

    if segment_mode == 'auto':
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            embedding = get_tongyi_embedding(para)
            KnowledgeChunk.objects.create(
                kb=kb,
                file=file_obj,
                content=para,
                embedding=json.dumps(embedding) if embedding else None,
                order=i
            )

    elif segment_mode == 'custom':
        words = text.split()
        i = 0
        order = 0
        while i < len(words):
            chunk_text = ' '.join(words[i:i + max_length])
            embedding = get_tongyi_embedding(chunk_text)
            KnowledgeChunk.objects.create(
                kb=kb,
                file=file_obj,
                content=chunk_text,
                embedding=json.dumps(embedding) if embedding else None,
                order=order
            )
            i += max_length
            order += 1

    elif segment_mode == 'hierarchical':
        lines = text.splitlines()
        current_parent = None
        order = 0
        for line in lines:
            if line.startswith("#"):
                embedding = get_tongyi_embedding(line.strip())
                current_parent = KnowledgeChunk.objects.create(
                    kb=kb,
                    file=file_obj,
                    content=line.strip(),
                    embedding=json.dumps(embedding) if embedding else None,
                    order=order
                )
            elif line.strip():
                embedding = get_tongyi_embedding(line.strip())
                KnowledgeChunk.objects.create(
                    kb=kb,
                    file=file_obj,
                    content=line.strip(),
                    embedding=json.dumps(embedding) if embedding else None,
                    order=order,
                    parent=current_parent
                )
            order += 1
    else:
        raise ValueError("不支持的分段方式")

@csrf_exempt
def get_text_content(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    uid = request.GET.get('uid')
    kb_id = request.GET.get('kb_id')
    text_id = request.GET.get('text_id')

    if not uid or not kb_id or not text_id:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 text_id 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    try:
        file = KnowledgeFile.objects.get(id=text_id, kb=kb)
    except KnowledgeFile.DoesNotExist:
        return JsonResponse({"code": -1, "message": "文件不存在或无权限"})

    chunks = KnowledgeChunk.objects.filter(file=file).order_by('order')

    content_list = []

    # 直接通过 parent 字段确定层级
    for chunk in chunks:
        if chunk.parent:
            # 如果有父级，则level为父级的order + 1
            level = chunk.parent.order + 1
        else:
            # 第一层的level是0
            level = 0

        content_list.append({
            "id": chunk.chunk_id,
            "level": level,
            "content": chunk.content
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "content": content_list
    })


def get_knowledge_bases(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    uid = request.GET.get('uid')
    if not uid:
        return JsonResponse({"code": -1, "message": "缺少 uid 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    kb_list = KnowledgeBase.objects.filter(user=user).order_by('-updated_at')

    knowledge_bases = []
    for kb in kb_list:
        knowledge_bases.append({
            "id": kb.kb_id,
            "type": kb.kb_type + "Base",
            "name": kb.kb_name,
            "description": kb.kb_description or "",
            "icon": kb.icon or "",  # 从数据库读取 icon 路径
            "updateTime": kb.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "createTime": kb.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "knowledgeBases": knowledge_bases
    })


ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']


@csrf_exempt
def upload_picture_kb_file(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    uid = request.POST.get('uid')
    kb_id = request.POST.get('kb_id')
    file = request.FILES.get('file')

    if not uid or not kb_id or not file:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 file 参数"})

    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse({"code": -1, "message": "不支持的文件类型"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    # 保存文件
    saved_file = KnowledgeFile.objects.create(
        kb=kb,
        file=file,
        name=file.name,
        segment_mode='auto'
    )

    # 生成智能标注
    label = get_image_caption(saved_file.file.path)

    if not label:
        label = f"图片文件: {saved_file.name}"  # 如果标注失败，兜底用文件名

    # 保存chunk
    KnowledgeChunk.objects.create(
        kb=kb,
        file=saved_file,
        content=label,
        embedding="[]",
        order=0
    )

    kb.updated_at = timezone.now()
    kb.save()

    return JsonResponse({
        "code": 0,
        "message": "上传成功"
    })


def get_image_caption(image_url):
    """
    输入公网图片URL，使用阿里云qwen-vl-plus生成图片描述。
    """

    try:
        # 正确初始化 client，api_key直接从 settings
        client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,  # 👈 这里！用settings，不用os.getenv
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            model="qwen-vl-plus",  # 阿里云视觉大模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请简要描述这张图片。"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        )

        # 提取并返回描述文本
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"[阿里云智能标注失败] {str(e)}")
        return None


def get_image_embedding(image_path):
    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/image-embedding/image-embedding"
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with open(image_path, 'rb') as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        payload = {
            "model": "image-embedding-v1",  # 这里要指定正确模型
            "input": {
                "image": img_base64
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        if "output" in data and "embeddings" in data["output"]:
            return data["output"]["embeddings"][0]
        else:
            print(f"[阿里云图像嵌入异常返回] {data}")
            return None

    except Exception as e:
        print(f"[阿里云图像嵌入失败] {str(e)}")
        return None


@csrf_exempt
def get_pictures(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    uid = request.GET.get('uid')
    kb_id = request.GET.get('kb_id')

    if not uid or not kb_id:
        return JsonResponse({"code": -1, "message": "缺少 uid 或 kb_id 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    # 获取该知识库下所有上传的图片文件
    picture_files = kb.files.all()

    pictures = []
    for file in picture_files:
        ext = os.path.splitext(file.name)[-1].lower()
        if ext in ALLOWED_IMAGE_EXTENSIONS:
            # 查找这个文件对应的chunk，提取描述内容
            chunk = KnowledgeChunk.objects.filter(file=file).first()

            pictures.append({
                "id": file.id,
                "name": file.name,
                "url": file.file.url,
                "description": chunk.content if chunk else f"图片文件：{file.name}"
            })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "pictures": pictures
    })

def preprocess_text(text):
    if not text:
        return ""

    # 去除过多的换行、控制字符
    text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    # 只保留可打印字符
    text = ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '。！？；：，、——（）【】')
    # 截断最大长度
    max_length = 4000
    return text[:max_length]

ALLOWED_TABLE_EXTENSIONS = ['.csv', '.xlsx']
@csrf_exempt
def upload_table_kb_file(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    uid = request.POST.get('uid')
    kb_id = request.POST.get('kb_id')
    file = request.FILES.get('file')

    if not uid or not kb_id or not file:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 file 参数"})

    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in ALLOWED_TABLE_EXTENSIONS:
        return JsonResponse({"code": -1, "message": "不支持的文件类型"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    kb.updated_at = timezone.now()
    kb.save()

    # 获取当前表格文件
    table_files = kb.files.filter(Q(name__iendswith='.csv') | Q(name__iendswith='.xlsx'))

    try:
        new_df = pd.read_csv(file) if ext == '.csv' else pd.read_excel(file)

        if table_files.exists():
            # 有已有表格，取第一个（按你的要求只允许一个表格）
            existing_file = table_files.first()
            existing_path = existing_file.file.path
            existing_ext = os.path.splitext(existing_path)[-1].lower()
            existing_df = pd.read_csv(existing_path) if existing_ext == '.csv' else pd.read_excel(existing_path)

            # 确保表头一致
            if list(existing_df.columns) != list(new_df.columns):
                return JsonResponse({"code": -1, "message": "表头不一致"})

            # 拼接表格
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # 覆盖保存文件
            save_path = existing_file.file.path
            if existing_ext == '.csv':
                combined_df.to_csv(save_path, index=False)
            else:
                combined_df.to_excel(save_path, index=False)

            # 只增加新增部分的 chunks
            start_order = existing_df.shape[0]
            for i, row in new_df.iterrows():
                row_text = ', '.join([f"{col}: {row[col]}" for col in new_df.columns])
                embedding = get_tongyi_embedding(row_text)
                if embedding:
                    KnowledgeChunk.objects.create(
                        kb=kb,
                        file=existing_file,
                        content=row_text,
                        embedding=json.dumps(embedding),
                        order=start_order + i
                    )

        else:
            # 没有表格文件，新建
            saved_file = KnowledgeFile.objects.create(
                kb=kb,
                file=file,
                name=file.name,
                segment_mode='auto'
            )

            for i, row in new_df.iterrows():
                row_text = ', '.join([f"{col}: {row[col]}" for col in new_df.columns])
                embedding = get_tongyi_embedding(row_text)
                if embedding:
                    KnowledgeChunk.objects.create(
                        kb=kb,
                        file=saved_file,
                        content=row_text,
                        embedding=json.dumps(embedding),
                        order=i
                    )

    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"上传成功但处理失败: {str(e)}"
        })

    return JsonResponse({
        "code": 0,
        "message": "上传成功"
    })

@csrf_exempt
def get_table_data(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    uid = request.GET.get('uid')
    kb_id = request.GET.get('kb_id')

    if not uid or not kb_id:
        return JsonResponse({"code": -1, "message": "缺少 uid 或 kb_id 参数"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    table_file = kb.files.filter(Q(name__iendswith='.csv') | Q(name__iendswith='.xlsx')).first()
    if not table_file:
        return JsonResponse({"code": -1, "message": "未找到任何表格文件"})

    try:
        file_path = table_file.file.path
        ext = os.path.splitext(file_path)[-1].lower()
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)

        columns = list(df.columns)
        data = df.fillna("").to_dict(orient='records')

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "columns": columns,
            "data": data
        })

    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"读取表格失败: {str(e)}"
        })

@csrf_exempt
def update_table(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST
        uid = body.get('uid')
        kb_id = body.get('kb_id')
        row_index = body.get('rowIndex')
        prop = body.get('prop')
        value = body.get('value')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or not kb_id:
        return JsonResponse({"code": -1, "message": "缺少 uid 或 kb_id 参数"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    table_file = kb.files.filter(Q(name__iendswith='.csv') | Q(name__iendswith='.xlsx')).first()
    if not table_file:
        return JsonResponse({"code": -1, "message": "未找到任何表格文件"})

    try:
        file_path = table_file.file.path
        ext = os.path.splitext(file_path)[-1].lower()
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)

        # 更新指定行列
        if int(row_index) >= len(df):
            return JsonResponse({"code": -1, "message": "行索引超出范围"})
        if prop not in df.columns:
            return JsonResponse({"code": -1, "message": "字段不存在"})

        df.at[int(row_index), prop] = value

        # 保存回文件
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)

        # 更新 KnowledgeChunk
        row_text = ', '.join([f"{col}: {df.at[int(row_index), col]}" for col in df.columns])
        embedding = get_tongyi_embedding(row_text)
        if embedding:
            # 找到对应 chunk 并更新
            chunk = KnowledgeChunk.objects.filter(
                kb=kb, file=table_file, order=int(row_index)
            ).first()
            if chunk:
                chunk.content = row_text
                chunk.embedding = json.dumps(embedding)
                chunk.save()

        kb.updated_at = timezone.now()
        kb.save()

        return JsonResponse({"code": 0, "message": "更新成功"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"更新失败: {str(e)}"})

@csrf_exempt
def add_table_row(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST

        uid = body.get('uid')
        kb_id = body.get('kb_id')
        row_data = body.get('rowData')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or not kb_id or not row_data:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 rowData 参数"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    table_file = kb.files.filter(Q(name__iendswith='.csv') | Q(name__iendswith='.xlsx')).first()
    if not table_file:
        return JsonResponse({"code": -1, "message": "未找到任何表格文件"})

    try:
        file_path = table_file.file.path
        ext = os.path.splitext(file_path)[-1].lower()
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)

        # 将 row_data 转为 DataFrame 并追加到现有 DataFrame
        new_row_df = pd.DataFrame([row_data])
        df = pd.concat([df, new_row_df], ignore_index=True)

        # 保存文件
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)

        # 构造新行文本
        new_index = len(df) - 1
        row_text = ', '.join([f"{col}: {df.at[new_index, col]}" for col in df.columns])
        embedding = get_tongyi_embedding(row_text)

        # 保存新的 chunk
        if embedding:
            KnowledgeChunk.objects.create(
                kb=kb,
                file=table_file,
                content=row_text,
                embedding=json.dumps(embedding),
                order=new_index
            )

        # 更新知识库更新时间
        kb.updated_at = timezone.now()
        kb.save()

        return JsonResponse({"code": 0, "message": "新增成功"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"新增失败: {str(e)}"})

@csrf_exempt
def delete_table_rows(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST

        uid = body.get('uid')
        kb_id = body.get('kb_id')
        rows = body.get('rows')  # 应为数组
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or not kb_id or rows is None:
        return JsonResponse({"code": -1, "message": "缺少 uid、kb_id 或 rows 参数"})

    if not isinstance(rows, list):
        return JsonResponse({"code": -1, "message": "rows 参数应为数组"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    table_file = kb.files.filter(Q(name__iendswith='.csv') | Q(name__iendswith='.xlsx')).first()
    if not table_file:
        return JsonResponse({"code": -1, "message": "未找到任何表格文件"})

    try:
        file_path = table_file.file.path
        ext = os.path.splitext(file_path)[-1].lower()
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)

        # 检查索引合法性
        if any(idx >= len(df) or idx < 0 for idx in rows):
            return JsonResponse({"code": -1, "message": "行索引超出范围"})

        # 删除指定行
        df = df.drop(rows).reset_index(drop=True)

        # 保存回文件
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)

        # 删除对应的 chunks
        KnowledgeChunk.objects.filter(kb=kb, file=table_file, order__in=rows).delete()

        # 重新调整剩余 chunks 的 order
        remaining_chunks = KnowledgeChunk.objects.filter(kb=kb, file=table_file).order_by('order')
        for new_order, chunk in enumerate(remaining_chunks):
            chunk.order = new_order
            chunk.save()

        # 更新知识库更新时间
        kb.updated_at = timezone.now()
        kb.save()

        return JsonResponse({"code": 0, "message": "删除成功"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"删除失败: {str(e)}"})

@csrf_exempt
def delete_resource(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        if request.content_type == "application/json":
            body = json.loads(request.body)
            uid = body.get('uid')
            resource_id = body.get('resource_id')
            resource_type = body.get('resource_type')
        else:
            uid = request.POST.get('uid')
            resource_id = request.POST.get('resource_id')
            resource_type = request.POST.get('resource_type')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if not uid or not resource_id or not resource_type:
        return JsonResponse({"code": -1, "message": "缺少必要参数 (uid、resource_id 或 resource_type)"})
    if resource_type == "workflow":
        try:
            if not uid or not resource_id:
                return JsonResponse({"code": -1, "message": "缺少参数 uid 或 workflow_id"})

            # 查找该用户下的 workflow
            try:
                workflow = Workflow.objects.get(workflow_id=resource_id, user__user_id=uid)
                workflow.delete()
                return JsonResponse({"code": 0, "message": "删除成功"})
            except Workflow.DoesNotExist:
                return JsonResponse({"code": -1, "message": "未找到对应的工作流"})

        except Exception as e:
            return JsonResponse({"code": -1, "message": str(e)})
    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        # 根据resource_id直接找KnowledgeBase
        kb = KnowledgeBase.objects.get(kb_id=resource_id, user=user)
    except KnowledgeBase.DoesNotExist:
        return JsonResponse({"code": -1, "message": "知识库不存在或无权限"})

    try:
        if resource_type in ['textBase', 'pictureBase', 'tableBase']:
            # 1. 删除知识库下所有的KnowledgeChunk
            KnowledgeChunk.objects.filter(kb=kb).delete()

            # 2. 删除知识库下所有的KnowledgeFile
            files = KnowledgeFile.objects.filter(kb=kb)
            for f in files:
                if f.file and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
                f.delete()

            # 3. 删除KnowledgeBase本身
            kb.delete()

        else:
            return JsonResponse({"code": -1, "message": f"不支持的资源类型: {resource_type}"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"删除失败: {str(e)}"})

    return JsonResponse({
        "code": 0,
        "message": "删除成功"
    })

@csrf_exempt
def delete_picture(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        kb_id = data.get('kb_id')
        picture_id = data.get('picture_id')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if not uid or not kb_id or not picture_id:
        return JsonResponse({"code": -1, "message": "缺少必要参数 (uid、kb_id、picture_id)"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    try:
        file = KnowledgeFile.objects.get(id=picture_id, kb=kb)
    except KnowledgeFile.DoesNotExist:
        return JsonResponse({"code": -1, "message": "图片文件不存在"})

    # 删除文件物理文件
    if file.file and os.path.isfile(file.file.path):
        os.remove(file.file.path)

    # 删除对应的chunk
    KnowledgeChunk.objects.filter(file=file).delete()

    # 删除文件记录
    file.delete()

    kb.updated_at = timezone.now()
    kb.save()

    return JsonResponse({
        "code": 0,
        "message": "删除成功"
    })

@csrf_exempt
def update_picture(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        kb_id = data.get('kb_id')
        picture_id = data.get('picture_id')
        description = data.get('description')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if not uid or not kb_id or not picture_id or description is None:
        return JsonResponse({"code": -1, "message": "缺少必要参数 (uid、kb_id、picture_id、description)"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    try:
        file = KnowledgeFile.objects.get(id=picture_id, kb=kb)
    except KnowledgeFile.DoesNotExist:
        return JsonResponse({"code": -1, "message": "图片文件不存在"})

    kb.updated_at = timezone.now()
    kb.save()

    # 更新chunk里的content
    chunk = KnowledgeChunk.objects.filter(file=file).first()
    if chunk:
        chunk.content = description
        chunk.save()
        return JsonResponse({
            "code": 0,
            "message": "编辑成功"
        })
    else:
        return JsonResponse({
            "code": -1,
            "message": "未找到对应标注"
        })

@csrf_exempt
def delete_text(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        kb_id = data.get('kb_id')
        text_id = data.get('text_id')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if not uid or not kb_id or not text_id:
        return JsonResponse({"code": -1, "message": "缺少必要参数 (uid、kb_id、text_id)"})

    try:
        user = User.objects.get(user_id=uid)
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except (User.DoesNotExist, KnowledgeBase.DoesNotExist):
        return JsonResponse({"code": -1, "message": "用户或知识库不存在或无权限"})

    try:
        file = KnowledgeFile.objects.get(id=text_id, kb=kb)
    except KnowledgeFile.DoesNotExist:
        return JsonResponse({"code": -1, "message": "文本文件不存在"})

    # 删除文件物理文件
    if file.file and os.path.isfile(file.file.path):
        os.remove(file.file.path)

    # 删除对应的chunk
    KnowledgeChunk.objects.filter(file=file).delete()

    # 删除文件记录
    file.delete()

    kb.updated_at = timezone.now()
    kb.save()

    return JsonResponse({
        "code": 0,
        "message": "删除成功"
    })

def workflow_run(request):
    data = json.loads(request.body)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    user_id = data.get("user_id")
    workflow_id = data.get("workflowId")

    executor = Executor(user_id, workflow_id, nodes, edges)
    result = executor.execute()
    return JsonResponse({"result": result})

@csrf_exempt
def workflow_create(request):
    try:
        uid = request.POST.get('uid')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.FILES.get('icon')  # 上传的文件

        # 查找用户
        try:
            user = User.objects.get(user_id=uid)
        except User.DoesNotExist:
            return JsonResponse({
                "code": -1,
                "message": "用户不存在",
                "workflow_id": None
            })

        # 初始化 icon_url（直接赋默认值）
        icon_url = "/media/workflow_icons/defaultWorkFlow.svg"

        if icon:
            # 构建图标存储路径
            icon_dir = os.path.join(settings.MEDIA_ROOT, 'workflow_icons')
            os.makedirs(icon_dir, exist_ok=True)

            # 构造唯一文件名
            _, ext = os.path.splitext(icon.name)
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(icon_dir, filename)

            # 写入图标文件
            with open(filepath, 'wb+') as destination:
                for chunk in icon.chunks():
                    destination.write(chunk)

            # 更新 icon 的 URL
            icon_url = f"/media/workflow_icons/{filename}"

        # 创建 Workflow 实例
        workflow = Workflow.objects.create(
            user=user,
            name=name,
            description=description,
            icon_url=icon_url,  # 无论是否上传，都有值
            nodes=json.dumps([]),  # ✅ 初始化为空数组
            edges=json.dumps([])
        )

        return JsonResponse({
            "code": 0,
            "message": "创建成功",
            "workflow_id": workflow.workflow_id
        })

    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"服务器错误：{str(e)}",
            "workflow_id": None
        })

def workflow_fetch(request):
    uid = request.GET.get('uid')
    workflow_id = request.GET.get('workflow_id')

    if not uid or not workflow_id:
        return JsonResponse({
            "code": -1,
            "message": "参数缺失",
        })

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在",
        })

    try:
        workflow = Workflow.objects.get(workflow_id=workflow_id, user=user)
    except Workflow.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "工作流不存在",
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "nodes": json.loads(workflow.nodes or '[]'),
        "edges": json.loads(workflow.edges or '[]'),
        "icon": workflow.icon_url,
        "name": workflow.name,
        "descript": workflow.description
    })


def workflow_save(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        uid = data.get("uid")
        workflow_id = data.get("workflow_id")
        nodes = json.dumps(data.get("nodes"))
        edges = json.dumps(data.get("edges"))

        if not uid or not workflow_id:
            return JsonResponse({"code": -1, "message": "uid 或 workflow_id 缺失"})

        try:
            user = User.objects.get(user_id=uid)
        except User.DoesNotExist:
            return JsonResponse({"code": -1, "message": "用户不存在"})

        try:
            workflow = Workflow.objects.get(workflow_id=workflow_id, user=user)
        except Workflow.DoesNotExist:
            return JsonResponse({"code": -1, "message": "工作流不存在"})

        workflow.nodes = nodes
        workflow.edges = edges
        workflow.save()

        return JsonResponse({"code": 0, "message": "保存成功"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": f"服务器错误：{str(e)}"})


def workflow_fetchAll(request):
    uid = request.GET.get('uid')
    if not uid:
        return JsonResponse({
            "code": -1,
            "message": "缺少用户ID",
            "workflows": []
        })

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在",
            "workflows": []
        })

    workflows = Workflow.objects.filter(user=user)
    workflow_list = []

    for workflow in workflows:
        workflow_list.append({
            "id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "icon": workflow.icon_url if workflow.icon_url else "",
            "updateTime":workflow.update_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "workflows": workflow_list
    })

def workflow_delete(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "请求方式错误，应为POST"})

    try:
        data = json.loads(request.body.decode('utf-8'))
        uid = data.get('uid')
        workflow_id = data.get('workflow_id')

        if not uid or not workflow_id:
            return JsonResponse({"code": -1, "message": "缺少参数 uid 或 workflow_id"})

        # 查找该用户下的 workflow
        try:
            workflow = Workflow.objects.get(workflow_id=workflow_id, user__user_id=uid)
            workflow.delete()
            return JsonResponse({"code": 0, "message": "删除成功"})
        except Workflow.DoesNotExist:
            return JsonResponse({"code": -1, "message": "未找到对应的工作流"})

    except Exception as e:
        return JsonResponse({"code": -1, "message": str(e)})

@csrf_exempt
def check_sensitive_words(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "仅支持 POST 请求"})

    try:
        data = json.loads(request.body)
        text = data.get('text', '')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    sensitive_words = SensitiveWord.objects.all()
    detected = [word.word_content for word in sensitive_words if word.word_content in text]

    if detected:
        return JsonResponse({
            "code": 1,
            "message": f"内容包含敏感词：{', '.join(detected)}",
            "detected_words": detected
        })
    else:
        return JsonResponse({
            "code": 0,
            "message": "未检测到敏感词"
        })

@csrf_exempt
def add_sensitive_word(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "仅支持 POST 请求"})

    try:
        data = json.loads(request.body)
        word_content = data.get('word')
        replacement = data.get('replacement', '')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if not word_content:
        return JsonResponse({"code": -1, "message": "缺少 word 参数"})

    if SensitiveWord.objects.filter(word_content=word_content).exists():
        return JsonResponse({"code": -1, "message": "敏感词已存在"})

    SensitiveWord.objects.create(word_content=word_content, replacement=replacement)
    return JsonResponse({"code": 0, "message": "敏感词添加成功"})

@csrf_exempt
def delete_sensitive_word(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "仅支持 POST 请求"})

    try:
        data = json.loads(request.body)
        word_id = data.get('id')
        word_content = data.get('word')
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"解析请求体失败: {str(e)}"})

    if word_id:
        try:
            word = SensitiveWord.objects.get(word_id=word_id)
            word.delete()
            return JsonResponse({"code": 0, "message": "敏感词删除成功（通过ID）"})
        except SensitiveWord.DoesNotExist:
            return JsonResponse({"code": -1, "message": "敏感词ID不存在"})
    elif word_content:
        try:
            word = SensitiveWord.objects.get(word_content=word_content)
            word.delete()
            return JsonResponse({"code": 0, "message": "敏感词删除成功（通过word）"})
        except SensitiveWord.DoesNotExist:
            return JsonResponse({"code": -1, "message": "敏感词不存在"})
    else:
        return JsonResponse({"code": -1, "message": "缺少 id 或 word 参数"})

@csrf_exempt
def list_sensitive_words(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "仅支持 GET 请求"})

    words = SensitiveWord.objects.all().values('word_id', 'word_content', 'replacement')
    word_list = list(words)

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "sensitive_words": word_list
    })


def agent_fetch_all(request):
    uid = request.GET.get('uid')

    if not uid:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agents = Agent.objects.filter(user=user).order_by('-agent_id')

        agent_list = []
        for agent in agents:
            # status 数字：0=private，1=under review，2=public
            if agent.status == 'published':
                status = 2
            elif agent.status == 'private':
                status = 0
            else:
                status = 1

            agent_list.append({
                "id": agent.agent_id,
                "icon": agent.icon_url,
                "name": agent.agent_name,
                "description": agent.description,
                "status": status,
                "publishedTime": agent.registered_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(agent, 'registered_at') and agent.registered_at else None
            })

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "agents": agent_list
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import User, Agent

@require_POST
def agent_release(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.decoder.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "传入参数格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)

        # 检查用户是否处于禁止发布状态
        post_message = check_user_post_status(user)
        if post_message:
            return JsonResponse({
                "code": -1,
                "message": post_message
            })

        agent = Agent.objects.get(agent_id=agent_id, user=user)

        # 发布操作：将状态置为 'check'（待审核）
        agent.status = 'check'
        agent.save()

        return JsonResponse({
            "code": 0,
            "message": "发布成功，待审核"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在或不属于该用户"
        })

def agent_remove(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.decoder.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "传入参数格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.get(agent_id=agent_id, user=user)

        agent.status = 'private'
        agent.save()

        return JsonResponse({
            "code": 0,
            "message": "下架成功"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在或不属于该用户"
        })

def agent_delete(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.decoder.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "传入参数格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.get(agent_id=agent_id, user=user)

        agent.delete()  # 彻底删除该智能体记录

        return JsonResponse({
            "code": 0,
            "message": "删除成功"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在或不属于该用户"
        })



def community_agent_fetch_basic_info(request):
    agent_id = request.GET.get('agent_id')
    if not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 agent_id 参数"
        })

    try:
        agent = Agent.objects.select_related('user').get(agent_id=agent_id)
        user = agent.user  # 外键字段
        data = {
            "code": 0,
            "message": "获取成功",
            "basicInfo": {
                "id": agent.agent_id,
                "name": agent.agent_name,
                "description": agent.description,
                "icon": agent.icon_url,
                "author": {
                    "id": user.user_id,
                    "account": user.email,
                    "name": user.username,  # 如果你有真实姓名字段可替换这里
                    "avatar": user.avatar_url
                },
                "stats": {
                    "usage": 0,  # 按你要求置为 0
                    "likes": agent.likes_count,
                    "favorites": agent.favorites_count
                }
            }
        }
        return JsonResponse(data)
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "Agent 不存在"
        })

def community_agent_fetch_user_actions(request):
    uid = request.GET.get('uid')
    agent_id = request.GET.get('agent_id')

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.select_related('user').get(agent_id=agent_id)
        author = agent.user  # 智能体作者

        # 查询是否点赞或收藏
        try:
            interaction = UserInteraction.objects.get(user=user, agent=agent)
            is_liked = interaction.is_liked
            is_favorited = interaction.is_favorited
        except UserInteraction.DoesNotExist:
            is_liked = False
            is_favorited = False

        # 查询是否关注作者
        is_followed = FollowRelationship.objects.filter(follower=user, followee=author).exists()

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "actions": {
                "isLiked": is_liked,
                "isFavorited": is_favorited,
                "isFollowed": is_followed
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在"
        })


def community_agent_fetch_comments(request):
    agent_id = request.GET.get('agent_id')

    if not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 agent_id 参数"
        })

    try:
        agent = Agent.objects.get(agent_id=agent_id)
        comments = Comment.objects.select_related('user').filter(agent=agent).order_by('-comment_time')

        comment_list = []
        for comment in comments:
            comment_list.append({
                "id": comment.comment_id,
                "name": comment.user.username,  # 如果有昵称字段可以换成昵称
                "userId": comment.user.user_id,
                "userAccount": comment.user.email,
                "avatar": comment.user.avatar_url,
                "content": comment.content,
                "time": comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "comments": comment_list
        })

    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在"
        })

def community_agent_handle_like(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "json数据格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.get(agent_id=agent_id)

        interaction, created = UserInteraction.objects.get_or_create(user=user, agent=agent)

        if interaction.is_liked:
            # 取消点赞
            interaction.is_liked = False
            agent.likes_count = max(0, agent.likes_count - 1)
            message = "取消点赞成功"
        else:
            # 点赞
            interaction.is_liked = True
            agent.likes_count += 1
            message = "点赞成功"

        interaction.save()
        agent.save()

        return JsonResponse({
            "code": 0,
            "message": message
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在"
        })

def community_agent_handle_Favorite(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "json数据格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.get(agent_id=agent_id)

        interaction, created = UserInteraction.objects.get_or_create(user=user, agent=agent)

        if interaction.is_favorited:
            # 取消收藏
            interaction.is_favorited = False
            agent.favorites_count = max(0, agent.favorites_count - 1)
            message = "取消收藏成功"
        else:
            # 收藏
            interaction.is_favorited = True
            agent.favorites_count += 1
            message = "收藏成功"

        interaction.save()
        agent.save()

        return JsonResponse({
            "code": 0,
            "message": message
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在"
        })

def community_agent_handle_Follow(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        author_id = data.get('author_id')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "json数据格式错误"
        })

    if not uid or not author_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 author_id 参数"
        })

    if uid == author_id:
        return JsonResponse({
            "code": -1,
            "message": "不能关注自己"
        })

    try:
        follower = User.objects.get(user_id=uid)
        followee = User.objects.get(user_id=author_id)

        existing = FollowRelationship.objects.filter(follower=follower, followee=followee).first()

        if existing:
            # 取消关注
            existing.delete()
            message = "取消关注成功"
            follower.following_count = follower.following_count - 1
            follower.save()
            followee.fans_count = followee.fans_count - 1
            followee.save()
        else:
            # 添加关注
            FollowRelationship.objects.create(follower=follower, followee=followee)
            message = "关注成功"
            follower.following_count = follower.following_count + 1
            follower.save()
            followee.fans_count = followee.fans_count + 1
            followee.save()

        return JsonResponse({
            "code": 0,
            "message": message
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })

def community_agent_handle_copy(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "json数据格式错误"
        })

    if not uid or not agent_id:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 或 agent_id 参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        original_agent = Agent.objects.get(agent_id=agent_id)

        copied_agent = Agent.objects.create(
            agent_name=original_agent.agent_name + " - 副本",
            description=original_agent.description,
            opening_line=original_agent.opening_line,
            prompt=original_agent.prompt,
            persona=original_agent.persona,
            category=original_agent.category,
            icon_url=original_agent.icon_url,
            user=user,
            status='private',
            is_modifiable=True,
            likes_count=0,
            favorites_count=0
        )

        return JsonResponse({
            "code": 0,
            "message": "复制成功"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "原始智能体不存在"
        })

def community_agent_send_comment(request):
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        agent_id = data.get('agent_id')
        comment_content = data.get('comment')
    except json.JSONDecodeError:
        return JsonResponse({
            "code": -1,
            "message": "json数据格式错误"
        })

    if not uid or not agent_id or not comment_content:
        return JsonResponse({
            "code": -1,
            "message": "缺少必要参数"
        })

    try:
        user = User.objects.get(user_id=uid)
        agent = Agent.objects.get(agent_id=agent_id)

        Comment.objects.create(
            user=user,
            agent=agent,
            content=comment_content
        )

        return JsonResponse({
            "code": 0,
            "message": "发布成功"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Agent.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "智能体不存在"
        })

@csrf_exempt
def fetch_pending_agents(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    try:
        pending_agents = Agent.objects.filter(status='check')
        agents_list = []
        for agent in pending_agents:
            agents_list.append({
                "id": agent.agent_id,
                "name": agent.agent_name,
                "description": agent.description,
                "icon": agent.icon_url,
                "author": {
                    "id": agent.user.user_id,
                    "name": agent.user.username,
                    "avatar": agent.user.avatar_url
                }
            })
        return JsonResponse({
            "code": 0,
            "message": "获取成功",
            "agents": agents_list
        })
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"获取失败: {str(e)}"})

@csrf_exempt
def review_agent(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        body = json.loads(request.body.decode('utf-8'))
        uid = body.get('uid')
        agent_id = body.get('agent_id')
        action = body.get('action')
        category = body.get('category')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or not agent_id or not action:
        return JsonResponse({"code": -1, "message": "缺少必要参数"})

    if action not in ['approve', 'reject']:
        return JsonResponse({"code": -1, "message": "无效的操作类型"})

    if action == 'approve' and not category:
        return JsonResponse({"code": -1, "message": "通过操作需要提供类别"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "管理员用户不存在"})

    try:
        agent = Agent.objects.get(agent_id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({"code": -1, "message": "智能体不存在"})

    try:
        if action == 'approve':
            agent.status = 'published'
            agent.category = category  # 仅通过时修改类别
        elif action == 'reject':
            agent.status = 'private'

        agent.save()

        return JsonResponse({"code": 0, "message": "操作成功"})
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"操作失败: {str(e)}"})

@csrf_exempt
def fetch_all_published_agents(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    try:
        published_agents = Agent.objects.filter(status='published')
        agents_list = []
        for agent in published_agents:
            # 统计当前智能体的评论数
            comment_count = Comment.objects.filter(agent=agent).count()
            agents_list.append({
                "id": agent.agent_id,
                "name": agent.agent_name,
                "category": agent.category,
                "description": agent.description,
                "image": agent.icon_url,
                "likes": agent.likes_count,
                "favorites": agent.favorites_count,
                "comments": comment_count,  # 新增字段：评论数
                "author": {
                    "id": agent.user.user_id,
                    "name": agent.user.username,
                    "avatar": agent.user.avatar_url
                }
            })
        return JsonResponse({
            "code": 0,
            "message": "操作成功",
            "agents": agents_list
        })
    except Exception as e:
        return JsonResponse({"code": -1, "message": f"获取失败: {str(e)}"})

class FetchWorksView(View):

    def get(self, request):
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse(
                {"code": -1, "message": "缺少 uid 参数"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "uid 对应的用户不存在"},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )

        agents = Agent.objects.filter(user=user)

        data = []
        for a in agents:
            if a.status == 'published':
                data.append({
                    "id": a.agent_id,
                    "name": a.agent_name,
                    "category": a.category,
                    "description": a.description or "",
                    "image": a.icon_url or "",
                    "likes": a.likes_count,
                    "favorites": a.favorites_count,
                })

        return JsonResponse(
            {"code": 0, "message": "获取成功", "data": data},
            json_dumps_params={'ensure_ascii': False}
        )

class FetchLikesView(View):
    """
    GET /user/fetchLikes?uid=<user_id>
    返回该用户点赞的所有智能体
    """
    def get(self, request):
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse(
                {"code": -1, "message": "缺少 uid 参数"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "uid 对应的用户不存在"},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )

        interactions = (
            UserInteraction.objects
            .filter(user=user, is_liked=True)
            .select_related('agent', 'agent__user')
        )

        data = []
        for ui in interactions:
            a = ui.agent
            if a.status == 'published':
                author = a.user
                data.append({
                    "id": a.agent_id,
                    "name": a.agent_name,
                    "category": a.category,
                    "description": a.description or "",
                    "image": a.icon_url or "",
                    "likes": a.likes_count,
                    "favorites": a.favorites_count,
                    "author": {
                        "id": author.user_id,
                        "name": author.username,
                        "avatar": author.avatar_url or ""
                    }
                })

        return JsonResponse(
            {"code": 0, "message": "获取成功", "data": data},
            json_dumps_params={'ensure_ascii': False}
        )

class FetchFavoritesView(View):
    """
    GET /user/fetchFavorites?uid=<user_id>
    返回该用户点赞的所有智能体
    """
    def get(self, request):
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse(
                {"code": -1, "message": "缺少 uid 参数"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "uid 对应的用户不存在"},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )

        interactions = (
            UserInteraction.objects
            .filter(user=user, is_favorited=True)
            .select_related('agent', 'agent__user')
        )

        data = []
        for ui in interactions:
            a = ui.agent
            if a.status == 'published':
                author = a.user
                # 统计当前智能体的评论数
                comment_count = Comment.objects.filter(agent=a).count()
                data.append({
                    "id": a.agent_id,
                    "name": a.agent_name,
                    "category": a.category,
                    "description": a.description or "",
                    "image": a.icon_url or "",
                    "likes": a.likes_count,
                    "favorites": a.favorites_count,
                    "comments": comment_count,  # 新增字段
                    "author": {
                        "id": author.user_id,
                        "name": author.username,
                        "avatar": author.avatar_url or ""
                    }
                })

        return JsonResponse(
            {"code": 0, "message": "获取成功", "data": data},
            json_dumps_params={'ensure_ascii': False}
        )

class FetchHotView(View):
    """
    GET /user/fetchHot
    返回按热度（likes_count + favorites_count）排序的智能体列表
    """

    def get(self, request):
        try:
            hot_agents = (
                Agent.objects
                .annotate(hot_score=ExpressionWrapper(
                    F('likes_count') + F('favorites_count') * 10,
                    output_field=IntegerField()
                ))
                .order_by('-hot_score')
                .select_related('user')
            )

            data = []
            for a in hot_agents:
                if a.status == 'published':
                    author = a.user
                    # 统计当前智能体的评论数
                    comment_count = Comment.objects.filter(agent=a).count()
                    data.append({
                        "id": a.agent_id,
                        "name": a.agent_name,
                        "category": a.category,
                        "description": a.description or "",
                        "image": a.icon_url or "",
                        "likes": a.likes_count,
                        "favorites": a.favorites_count,
                        "comments": comment_count,  # 新增字段
                        "author": {
                            "id": author.user_id,
                            "name": author.username,
                            "avatar": author.avatar_url or ""
                        }
                    })

            return JsonResponse(
                {"code": 0, "message": "获取成功", "data": data},
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            return JsonResponse(
                {"code": -1, "message": f"获取失败：{str(e)}"},
                status=500,
                json_dumps_params={'ensure_ascii': False}
            )

class FetchFollowWorksView(View):
    """
    GET /user/fetchFollowWorks?uid=<user_id>
    返回该用户关注的所有用户发布的智能体列表
    """
    def get(self, request):
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse(
                {"code": -1, "message": "缺少 uid 参数"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "uid 对应的用户不存在"},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )

        followees = FollowRelationship.objects.filter(follower=user).values_list('followee', flat=True)

        agents = (
            Agent.objects
                 .filter(user_id__in=followees)
                 .select_related('user')
        )

        data = []
        for a in agents:
            if a.status == 'published':
                author = a.user
                # 统计当前智能体的评论数
                comment_count = Comment.objects.filter(agent=a).count()
                data.append({
                    "id": a.agent_id,
                    "name": a.agent_name,
                    "category": a.category,
                    "description": a.description or "",
                    "image": a.icon_url or "",
                    "likes": a.likes_count,
                    "favorites": a.favorites_count,
                    "comments": comment_count,  # 新增字段
                    "author": {
                        "id": author.user_id,
                        "name": author.username,
                        "avatar": author.avatar_url or ""
                    }
                })

        return JsonResponse(
            {"code": 0, "message": "获取成功", "data": data},
            json_dumps_params={'ensure_ascii': False}
        )

from api.core.workflow.registry import NODE_REGISTRY
from api.core.workflow.nodes import loader
def workflow_run_single(request):
    data = json.loads(request.body)
    try:
        workflow_id = data.get('workflow_id')
        node_id = int(data.get('node_id'))
        raw_inputs = data.get('inputs', '{}')  # JSON 字符串
        inputs = json.loads(raw_inputs)

        # 获取工作流
        workflow = Workflow.objects.get(workflow_id=workflow_id)
        nodes = json.loads(workflow.nodes)

        # 查找对应的节点
        node = next((n for n in nodes if n['id'] == node_id), None)
        if not node:
            return JsonResponse({"code": -1, "message": "节点未找到"})

        node_type = node.get("type")
        func = NODE_REGISTRY.get(node_type)
        if not func:
            return JsonResponse({"code": -2, "message": f"未注册的节点类型: {node_type}"})
        result = func(node,inputs)
        return JsonResponse({
            "code": 0,
            "message": "节点执行成功",
            "result": result
        })

    except Exception as e:
        return JsonResponse({
            "code": 1,
            "message": f"服务器错误: {str(e)}"
        })

# views.py
import re
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import User     # 根据实际路径调整
# =================================================================
# Admin-User 接口
# =================================================================

@csrf_exempt
def fetch_user(request):
    """接口1：获取用户列表（GET /admin/fetchUser）"""
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    users_data = []
    for u in User.objects.all().order_by('-registered_at'):
        users_data.append({
            "uid": u.user_id,
            "email": u.email,
            "name": u.username,
            "avatar": u.avatar_url or "",
            "can_log": (not u.is_banned),
            "can_post": u.can_post,
            "ban_expire": localtime(u.ban_expire).strftime("%Y-%m-%d %H:%M:%S") if u.ban_expire else "",
            "post_expire": localtime(u.post_expire).strftime("%Y-%m-%d %H:%M:%S") if u.post_expire else "",
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "users": users_data
    })


@csrf_exempt
def ban_user(request):
    """接口2：封禁用户（POST /admin/banUser）"""
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败，需 JSON 格式"})

    uid      = data.get('uid')
    ban_type = data.get('type')   # 'account' | 'post'
    time_str = data.get('time')   # '数字 单位'

    # ---------- 参数校验 ----------
    if not uid or not ban_type or not time_str:
        return JsonResponse({"code": -1, "message": "缺少 uid、type 或 time"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    # ---------- 解析时间 ----------
    m = re.fullmatch(r'\s*(\d+)\s*(年|月|日)\s*', time_str)
    if not m:
        return JsonResponse({"code": -1, "message": "time 格式应为“数字 单位（年|月|日）”"})

    num, unit = int(m.group(1)), m.group(2)
    now = timezone.now()
    if unit == '年':
        expire = now + relativedelta(years=num)
    elif unit == '月':
        expire = now + relativedelta(months=num)
    else:  # '日'
        expire = now + datetime.timedelta(days=num)

    # ---------- 更新用户状态 ----------
    if ban_type == 'account':
        user.is_banned  = True
        user.ban_expire = expire
    elif ban_type == 'post':
        user.can_post   = False
        user.post_expire = expire
    else:
        return JsonResponse({"code": -1, "message": "type 参数非法，应为 'account' 或 'post'"})

    user.save()
    return JsonResponse({"code": 0, "message": "封禁成功"})

@csrf_exempt
def unban_user(request):
    """接口3：解封用户（POST /admin/unbanUser）"""
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败，需 JSON 格式"})

    uid = data.get('uid')
    if not uid:
        return JsonResponse({"code": -1, "message": "缺少 uid"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    # 复位所有封禁状态
    user.is_banned   = False
    user.can_post    = True
    user.ban_expire  = None
    user.post_expire = None
    user.save()

    return JsonResponse({"code": 0, "message": "解封成功"})

@csrf_exempt
def report_agent(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body.decode('utf-8'))
        uid = data.get('uid')
        agent_id = data.get('agent_id')
        reason = data.get('reason')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not uid or not agent_id or not reason:
        return JsonResponse({"code": -1, "message": "缺少 uid、agent_id 或 reason 参数"})

    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        return JsonResponse({"code": -1, "message": "用户不存在"})

    try:
        agent = Agent.objects.get(agent_id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({"code": -1, "message": "被举报智能体不存在"})

    AgentReport.objects.create(
        reporter=user,
        agent=agent,
        reason=reason
    )

    return JsonResponse({"code": 0, "message": "举报成功"})

def get_agent_reports(request):
    if request.method != 'GET':
        return JsonResponse({"code": -1, "message": "只支持 GET 请求"})

    report_list = AgentReport.objects.select_related('reporter', 'agent').order_by('-report_time')

    reports = []
    for r in report_list:
        reports.append({
            "report_id": r.report_id,
            "reporter": r.reporter.username,
            "agent_id": r.agent.agent_id,
            "agent_name": r.agent.agent_name,
            "reason": r.reason,
            "is_processed": r.is_processed,
            "process_result": r.process_result,
            "processed_by": r.processed_by.account if r.processed_by else "",
            "report_time": r.report_time.strftime("%Y-%m-%d %H:%M:%S"),
            "processed_time": r.processed_time.strftime("%Y-%m-%d %H:%M:%S") if r.processed_time else ""
        })

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "reports": reports
    })

@csrf_exempt
def process_agent_report(request):
    if request.method != 'POST':
        return JsonResponse({"code": -1, "message": "只支持 POST 请求"})

    try:
        data = json.loads(request.body.decode('utf-8'))
        report_id = data.get('report_id')
        admin_id = data.get('admin_id')
        result = data.get('result')
    except Exception:
        return JsonResponse({"code": -1, "message": "请求体解析失败"})

    if not report_id or not admin_id or not result:
        return JsonResponse({"code": -1, "message": "缺少 report_id、admin_id 或 result 参数"})

    try:
        report = AgentReport.objects.get(report_id=report_id)
        admin = Administrator.objects.get(admin_id=admin_id)
    except (AgentReport.DoesNotExist, Administrator.DoesNotExist):
        return JsonResponse({"code": -1, "message": "举报记录或管理员不存在"})

    if report.is_processed:
        return JsonResponse({"code": -1, "message": "该举报已被处理"})

    report.is_processed = True
    report.process_result = result
    report.processed_by = admin
    report.processed_time = timezone.now()
    report.save()

    return JsonResponse({"code": 0, "message": "处理完成"})
