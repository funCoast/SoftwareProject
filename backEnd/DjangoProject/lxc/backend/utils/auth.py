import uuid, time
import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=getattr(settings, 'REDIS_DB', 0),
    decode_responses=True
)

def generate_and_cache_token(user_id: int, device: str | None = None) -> str:
    """
    生成随机 Token 并写入 token_<uid> 集合，维持 15 min 过期。
    可选 device 字段用来区分“iOS/Android/Web”等。
    """
    token = str(uuid.uuid4())
    key   = f"token_{user_id}"
    redis_client.sadd(key, token)                       # ➊ 加入集合
    redis_client.expire(key, settings.TOKEN_EXPIRE_SECONDS)

    # 可存更丰富的信息（示例）
    if device:
        info_key = f"token_info_{token}"
        redis_client.hmset(info_key, {
            "uid":     user_id,
            "device":  device,
            "iat":     int(time.time())
        })
        redis_client.expire(info_key, settings.TOKEN_EXPIRE_SECONDS)

    return token

def validate_token(uid: str, token: str) -> bool:
    """检查 Token 是否属于 uid 对应的集合。"""
    return redis_client.sismember(f"token_{uid}", token)

def prolong_token(uid: str):
    """滑动续期 —— 只需重设集合键 TTL。"""
    redis_client.expire(f"token_{uid}", settings.TOKEN_EXPIRE_SECONDS)

def revoke_token(uid: str, token: str):
    """仅踢当前端 Token。"""
    redis_client.srem(f"token_{uid}", token)
    redis_client.delete(f"token_info_{token}")     # 若存了 info

def revoke_all(uid: str):
    """踢下该用户所有端。"""
    key = f"token_{uid}"
    # 批量删除 token_info_*
    for tk in redis_client.smembers(key):
        redis_client.delete(f"token_info_{tk}")
    redis_client.delete(key)
