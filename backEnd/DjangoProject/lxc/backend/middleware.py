# backend/middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from backend.utils.auth import redis_client

EXEMPT_PATHS = {
    '/register',
    '/user/sendCode',
    '/user/loginByCode',
    '/user/loginByPassword',
    '/static/',            # 🌟 如有静态资源
    '/media/',             # 🌟 如有图片/文件
}

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 白名单放行
        for p in EXEMPT_PATHS:
            if request.path.startswith(p):
                return

        token = request.headers.get('token')
        uid   = request.headers.get('uid')
        if not token or not uid:
            return JsonResponse({'code': -2, 'message': '未登录或缺少凭证'}, status=401)

        cache_key = f'token_{uid}'
        if redis_client.get(cache_key) != token:
            return JsonResponse({'code': -2, 'message': '登录状态已失效'}, status=401)

        # 滑动过期
        redis_client.expire(cache_key, settings.TOKEN_EXPIRE_SECONDS)
        request.user_id = int(uid)   # 供视图直接使用
