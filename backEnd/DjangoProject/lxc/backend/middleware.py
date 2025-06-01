from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from backend.utils.auth import validate_token, prolong_token
from django.conf import settings

EXEMPT_PREFIXES = (
    '/user/loginByPassword', '/user/loginByCode',
    '/register', '/static/', '/media/', '/user/sendCode',
)

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 0. 白名单放行
        path = request.path.replace('/linksoul', '', 1)  # 如有前缀裁剪
        if any(path.startswith(p) for p in EXEMPT_PREFIXES):
            return

        # 1. 读取头部
        token = request.headers.get('token')
        uid   = request.headers.get('uid')
        if not token or not uid:
            return JsonResponse({'code': -2, 'message': '未登录'}, status=401)

        # 2. 校验
        if not validate_token(uid, token):
            return JsonResponse({'code': -2, 'message': '登录状态已失效'}, status=401)

        # 3. 滑动过期
        prolong_token(uid)
        request.user_id = int(uid)
