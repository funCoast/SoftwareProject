# backend/utils/auth.py
# -*- coding: utf-8 -*-
import uuid
import time
import redis
from typing import Optional          # 新增：兼容 Py 3.8 的类型注解
from django.conf import settings

# ─────────────────────────────── Redis 客户端 ────────────────────────────────
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=getattr(settings, "REDIS_DB", 0),
    decode_responses=True
)

# ────────────────────────────── 核心工具函数 ────────────────────────────────
def generate_and_cache_token(user_id: int,
                             device: Optional[str] = None) -> str:
    """
    生成随机 Token 并写入 token_<uid> 集合，维持 15 min 过期。
    可选 device 字段用来区分“iOS / Android / Web”等终端。
    """
    token = str(uuid.uuid4())
    key   = f"token_{user_id}"

    # ➊ 加入集合并设置统一 TTL
    redis_client.sadd(key, token)
    redis_client.expire(key, settings.TOKEN_EXPIRE_SECONDS)

    # ➋ 可选：记录设备信息，便于后台管理或限制并发端
    if device:
        info_key = f"token_info_{token}"
        redis_client.hmset(info_key, {
            "uid":    user_id,
            "device": device,
            "iat":    int(time.time())
        })
        redis_client.expire(info_key, settings.TOKEN_EXPIRE_SECONDS)

    return token


def validate_token(uid: str, token: str) -> bool:
    """检查 Token 是否属于 uid 对应集合。"""
    return redis_client.sismember(f"token_{uid}", token)


def prolong_token(uid: str) -> None:
    """滑动续期——重设集合键 TTL。"""
    redis_client.expire(f"token_{uid}", settings.TOKEN_EXPIRE_SECONDS)


def revoke_token(uid: str, token: str) -> None:
    """仅踢当前端 Token。"""
    redis_client.srem(f"token_{uid}", token)
    redis_client.delete(f"token_info_{token}")   # 若记录了 info


def revoke_all(uid: str) -> None:
    """踢下该用户所有端。"""
    key = f"token_{uid}"
    for tk in redis_client.smembers(key):        # 批量删除附加信息
        redis_client.delete(f"token_info_{tk}")
    redis_client.delete(key)
