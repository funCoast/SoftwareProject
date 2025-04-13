import uuid
import random
from smtplib import SMTPException

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse
# user/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json
# backend/views.py
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Announcement
from django.utils import timezone

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
def user_update_avatar(request):
    uid = request.POST.get('uid')
    avatar = request.FILES.get('avatar')

    if not uid or not avatar:
        return JsonResponse({
            "code": -1,
            "message": "uid 或 avatar 缺失"
        })

    try:
        user = User.objects.get(user_id=uid)  # 或 username/其他主键字段
        user.avatar = avatar  # 会自动保存到 avatars/ 路径下
        user.save()

        return JsonResponse({
            "code": 0,
            "message": "更新成功"
        })
    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在"
        })
    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": f"更新失败：{str(e)}"
        })


def user_get_avatar(request):
    uid = request.GET.get('uid')

    if not uid:
        return JsonResponse({
            "code": -1,
            "message": "缺少 uid 参数",
            "avatar": ""
        })

    try:
        user = User.objects.get(user_id=uid)  # 如果你用的是自定义 user_id 字段
    except User.DoesNotExist:
        return JsonResponse({
            "code": -1,
            "message": "用户不存在",
            "avatar": ""
        })

    avatar_url = user.avatar.url if user.avatar else ""

    return JsonResponse({
        "code": 0,
        "message": "获取成功",
        "avatar": avatar_url
    })

# Announcement

@api_view(['POST'])
def announcement_add(request):
    title = request.data.get('title')
    content = request.data.get('content')

    if not title or not content:
        return Response({
            'code': -1,
            'message': 'Title and content are required.',
            'announcements': []
        }, status=status.HTTP_400_BAD_REQUEST)

    announcement = Announcement.objects.create(
        title=title,
        content=content,
        time=timezone.now()
    )

    # 返回包含新公告的响应
    return Response({
        'code': 0,
        'message': '获取成功',
        'announcements': [{
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'time': announcement.time.isoformat()
        }]
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def announcement_update(request):
    announcement_id = request.data.get('id')
    title = request.data.get('title')
    content = request.data.get('content')

    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        return Response({
            'code': -1,
            'message': 'Announcement not found.',
            'announcements': []
        }, status=status.HTTP_404_NOT_FOUND)

    if title:
        announcement.title = title
    if content:
        announcement.content = content
    announcement.time = timezone.now()  # 更新修改时间
    announcement.save()

    return Response({
        'code': 0,
        'message': '获取成功',
        'announcements': [{
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'time': announcement.time.isoformat()
        }]
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def announcement_delete(request):
    announcement_id = request.data.get('id')

    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.delete()
        return Response({
            'code': 0,
            'message': '获取成功',
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
    announcements = Announcement.objects.all()
    if not announcements:
        return Response({
            'code': -1,
            'message': 'No announcements found.',
            'announcements': []
        }, status=status.HTTP_404_NOT_FOUND)

    data = [{
        'id': announcement.id,
        'title': announcement.title,
        'content': announcement.content,
        'time': announcement.time.isoformat()
    } for announcement in announcements]

    return Response({
        'code': 0,
        'message': '获取成功',
        'announcements': data
    })
