import os

import pika
from dotenv import load_dotenv

load_dotenv()

# Database config
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_db_url():
	return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


TG_SECRET = os.getenv("TG_SECRET")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")


# Setup RabbitMQ
def get_rabbit_connection():
	return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))


rabbit_channel = get_rabbit_connection().channel()
rabbit_channel.exchange_declare("reseller_exchange", exchange_type="direct")

# Queues
rabbit_channel.queue_declare("order_queue")
rabbit_channel.queue_declare("item_queue")

# Binding
rabbit_channel.queue_bind("order_queue", "reseller_exchange", "order_updates")
rabbit_channel.queue_bind("item_queue", "reseller_exchange", "item_updates")
