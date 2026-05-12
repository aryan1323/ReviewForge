import redis
from rq import Queue
from rq.job import Retry

from app.config import get_settings

settings = get_settings()

redis_conn = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
review_queue = Queue("reviews", connection=redis_conn, default_timeout=300)

__all__ = ["redis_conn", "review_queue"]
