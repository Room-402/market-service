import redis
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    ssl=settings.REDIS_SSL,
                    ssl_cert_reqs=None,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                cls._instance.ping()
                logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise e
        return cls._instance

def get_redis():
    return RedisClient.get_client()
