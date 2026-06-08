from redis import Redis
from psycopg import connect

from app.config import Settings


def check_postgres(settings: Settings) -> bool:
    with connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            return cursor.fetchone() == (1,)


def check_redis(settings: Settings) -> bool:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        return bool(client.ping())
    finally:
        client.close()
