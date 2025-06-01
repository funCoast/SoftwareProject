# backend/utils/auth.py
import uuid
import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=getattr(settings, "REDIS_DB", 0),
    decode_responses=True
)

def generate_and_cache_token(user_id: int) -> str:
    """
    生成随机 Token 并写入 Redis，键格式 token_<uid>，
    过期时间 settings.TOKEN_EXPIRE_SECONDS（15 分钟）
    """
    token = str(uuid.uuid4())
    redis_client.setex(f"token_{user_id}",
                       settings.TOKEN_EXPIRE_SECONDS,
                       token)
    return token
