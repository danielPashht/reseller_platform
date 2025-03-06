import os
import pika
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("reseller")
TG_SECRET = os.getenv("TG_SECRET")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")


def get_db_url():
	db_host = 'reseller_postgresql'  # os.getenv("DB_HOST", "localhost")
	db_port = os.getenv("DB_PORT", 5432)
	db_user = os.getenv("DB_USER", "postgres")
	db_password = os.getenv("DB_PASSWORD", "postgres")
	db_name = os.getenv("DB_NAME", "reseller")
	return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_rabbit_connection():
	credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
	parameters = pika.ConnectionParameters(
		host='reseller_rabbitmq',
		port=RABBITMQ_PORT,
		credentials=credentials,
		heartbeat=600,
		blocked_connection_timeout=300
	)
	return pika.BlockingConnection(parameters)


def setup_rabbitmq():
	_connection = get_rabbit_connection()
	_channel = _connection.channel()
	_channel.exchange_declare(exchange='reseller_exchange', exchange_type='direct')
	_channel.queue_declare(queue='order_queue')
	_channel.queue_declare(queue='item_queue')
	_channel.queue_bind(queue='order_queue', exchange='reseller_exchange', routing_key='order_updates')
	_channel.queue_bind(queue='item_queue', exchange='reseller_exchange', routing_key='item_updates')
	_channel.queue_bind(queue='item_queue', exchange='reseller_exchange', routing_key='item_deletes')

	return _connection, _channel


rabbit_connection, rabbit_channel = setup_rabbitmq()
