import redis
from config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=getattr(settings, "REDIS_USERNAME", None),
    password=getattr(settings, "REDIS_PASSWORD", None),
    ssl=getattr(settings, "REDIS_SSL", False),
    decode_responses=True
)