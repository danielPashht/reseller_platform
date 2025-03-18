import os
import logging
import pika
import redis
from dotenv import load_dotenv


load_dotenv()


logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)


BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_API_URL = os.getenv("ADMIN_API_URL")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

MANAGER_USER_ID = os.getenv("MANAGER_USER_ID")


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=int(RABBITMQ_PORT))
            )
            self.channel = self.connection.channel()
            # Ensure exchange exists (idempotent)
            self.channel.exchange_declare(
                exchange="reseller_exchange", exchange_type="direct"
            )
            logger.info("RabbitMQ connection established in bot")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def ensure_connection(self):
        if not self.connection or self.connection.is_closed:
            logger.warning("RabbitMQ connection closed, reconnecting...")
            self.connect()
        if not self.channel or self.channel.is_closed:
            logger.warning("RabbitMQ channel closed, recreating...")
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange="reseller_exchange", exchange_type="direct"
            )


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
    )


rabbitmq_client = RabbitMQClient()
redis_client = get_redis_client()
