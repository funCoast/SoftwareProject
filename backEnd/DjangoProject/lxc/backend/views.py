from django.http import HttpResponse
# user/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import User
import json


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
