import uuid

from django.core.mail import EmailMessage
from django.http import HttpResponse
# user/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import User
import json
# backend/views.py
from django.conf import settings
import redis
from rest_framework.decorators import api_view

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
    try:
        email = request.data.get('email', None)
        # TODO 前端判断邮箱格式？

        # TODO 每分钟只能发送一次，前端？
        if redis_client.exists(f'verification_code_{email}'):
            return JsonResponse({
                'code': -1,
                'message': '验证码已发送，请稍后再试'
            })

        # TODO 生成验证码
        code = '123456'

        # 将验证码存储到 Redis 中，设置过期时间为 5 分钟
        redis_client.setex(f'verification_code_{email}', 300, code)

        # TODO 发送验证码到用户邮箱
        # subject = '您的验证码'
        # body = f'【灵犀AI社区】您的验证码是：{code}，请在5分钟内使用。'
        # email_message = EmailMessage(
        #     subject=subject,
        #     body=body,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     to=[email]
        # )
        # email_message.send()

        return JsonResponse({
            'code': 0,
            'message': f'已发送'
        })

    except Exception as e:
        # 解析异常
        return JsonResponse({
            'code': -1,
            'message': str(e)
        })

'''
用户登录接口
'''
def user_login_by_code(request):
    try:
        email = request.POST.get('email', None)
        code = request.POST.get('code', None)

        # TODO 验证邮箱格式？

        # TODO 验证验证码
        stored_code = redis_client.get(f'verification_code_{email}')
        if not stored_code or stored_code != code:
            return JsonResponse({
                'code': -1,
                'message': '验证码不正确或已过期'
            })

        # 删除Redis中的验证码
        redis_client.delete(f'verification_code_{email}')

        # 生成登录token
        token = str(uuid.uuid4())
        user_id = 123  # 这里应该从数据库中获取实际的用户ID

        # 将token存储到Redis中，设置过期时间为30分钟
        redis_client.setex(f'token_{user_id}', 1800, token)

        # TODO 返回成功响应json
        return JsonResponse({
            'code': 0,
            'message': '登录成功',
            'token': '',
            'id': ''
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

        # TODO 验证邮箱格式

        # 获取用户信息
        try:
            user = User.objects.get(email=account)
        except User.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'message': f'用户不存在'
            })

        # 验证密码
        if user.password != password:
            return JsonResponse({
                'code': -1,
                'message': '2密码错误'
            })

        # 生成登录token
        token = str(uuid.uuid4())
        user_id = user.user_id

        # 将token存储到Redis中，设置过期时间为30分钟
        redis_client.setex(f'token_{user_id}', 1800, token)

        # 返回成功响应
        return JsonResponse({
            'code': 0,
            'message': '3登录成功',
            'token': token,
            'id': user_id
        })

    except Exception as e:
        return JsonResponse({
            'code': -1,
            'message': "4" + str(e)
        })