import redis
from utilities.settings import setting


def get_rds():
    rds = redis.Redis(
        host=setting.redis_host, port=setting.redis_port, db=setting.redis_db
    )
    try:
        yield rds
    finally:
        rds.close()
