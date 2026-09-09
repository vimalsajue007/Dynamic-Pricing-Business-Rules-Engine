import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger("pricing_engine")

try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
except Exception:  # pragma: no cover
    redis_client = None


def cache_get(key: str) -> Optional[Any]:
    if redis_client is None:
        return None
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis GET failed for key=%s: %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = settings.REDIS_TTL_SECONDS) -> None:
    if redis_client is None:
        return
    try:
        redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis SET failed for key=%s: %s", key, exc)


def cache_delete_prefix(prefix: str) -> None:
    if redis_client is None:
        return
    try:
        for key in redis_client.scan_iter(f"{prefix}*"):
            redis_client.delete(key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis DELETE prefix=%s failed: %s", prefix, exc)
