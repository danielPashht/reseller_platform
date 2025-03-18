from typing import Dict, List
import httpx
import asyncio
import logging
import threading
from bot.db.schemas import ItemDeleteMessage, ItemUpdateMessage
from bot.config import ADMIN_API_URL, ADMIN_API_KEY, redis_client, rabbitmq_client
import json
from pydantic import ValidationError

logger = logging.Logger("bot")


class DataStorage:
    """
    Manages data storage and retrieval for items, carts, and order information.

    This class interacts with Redis for caching and persistent storage,
    the backend API for initial item loading, and RabbitMQ for real-time item updates.
    It also handles cart operations and manages the local cache of items.

    Attributes:
        ITEM_QUEUE (str): The name of the RabbitMQ queue for item update messages.
        _items (List[Dict]): A local cache of items loaded from Redis.
        _items_lock (threading.Lock): A lock to ensure thread safety when accessing
            and modifying the `_items` list.
        redis_client: The Redis client instance for interacting with Redis.
        rabbit_client: The RabbitMQ client instance for interacting with RabbitMQ.
        consumer_thread (threading.Thread): Thread, that starts rabbit consumer.
    """
    ITEM_QUEUE = "item_queue"

    def __init__(self):
        self._items: List[Dict] = []
        self._items_lock = threading.Lock()
        self.redis_client = redis_client
        self.rabbit_client = rabbitmq_client

        self.set_item_consumption()
        self.consumer_thread = threading.Thread(
            target=self._start_consuming_sync, daemon=True
        )
        self.consumer_thread.start()

    async def fetch_items(self):
        """Used on app start to fetch items from backend and store them to redis"""
        headers = {"X-API-Key": ADMIN_API_KEY}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{ADMIN_API_URL}/items/", headers=headers)
                response.raise_for_status()
                items = response.json()
                self.store_items_in_redis(items)
                logger.info(
                    f"Fetched {len(items)} items from admin API and stored in Redis"
                )
            except httpx.HTTPError as e:
                logger.error(f"Error loading items from admin API: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from admin API: {e}")

    def store_item(self, new_item: Dict):
        """Stores or updates an item in Redis and updates the local cache."""
        try:
            item_key = self._get_item_key(new_item["id"])
            self.redis_client.set(item_key, json.dumps(new_item))

            with self._items_lock:
                existing_item_index = next(
                    (
                        i for i, item in enumerate(self._items)
                        if item["id"] == new_item["id"]
                    ),
                    None,
                )
                if existing_item_index is not None:
                    self._items[existing_item_index] = new_item
                else:
                    self._items.append(new_item)
            logger.info(f"Updated item {new_item['id']} in Redis and local cache")

        except Exception as e:
            logger.error(f"Error in store_item: {e}")

    def delete_item(self, item_id: int):
        """Deletes an item from Redis and the local cache."""
        try:
            # Validate item_id type
            if not isinstance(item_id, int):
                raise TypeError(f"item_id must be an integer, got {type(item_id)}")

            item_key = self._get_item_key(item_id)
            deleted_count = self.redis_client.delete(item_key)
            if deleted_count == 0:
                logger.warning(
                    f"Item with ID {item_id} not found in Redis for deletion"
                )
                return

            with self._items_lock:
                self._items = [item for item in self._items if item["id"] != item_id]
            logger.info(f"Deleted item with ID {item_id} from Redis and local cache")

        except TypeError as e:
            logger.error(f"Invalid item_id type: {e}")
        except Exception as e:
            logger.error(f"Error in delete_item: {e}")

    async def get_all_items(self) -> List[Dict]:
        """
        Retrieves all stored items:
        uses self._items if populated and fresh, otherwise fetches from redis
        """
        with self._items_lock:
            if self._items:
                return self._items.copy()

        try:
            item_keys = self.redis_client.keys("item:*")
            if not item_keys:
                return []
            pipeline = self.redis_client.pipeline()
            for key in item_keys:
                pipeline.get(key)
            results = pipeline.execute()
            items = [json.loads(item) for item in results if item]
            with self._items_lock:
                self._items = items.copy()
            return items
        except Exception as e:
            logger.error(f"Error in get_all_items: {e}")
            return []

    def store_items_in_redis(self, items: List[Dict]):
        """Stores items in Redis."""
        try:
            pipeline = self.redis_client.pipeline()
            for item in items:
                pipeline.set(self._get_item_key(item["id"]), json.dumps(item))
            pipeline.execute()
            logger.info(f"Successfully stored {len(items)} items in redis")
        except Exception as e:
            logger.error(f"Error in store_items_in_redis: {e}")

    @staticmethod
    def _get_item_key(item_id: int) -> str:
        return f"item:{item_id}"

    def set_item_consumption(self):
        """Set up RabbitMQ consumption for item updates"""
        self.rabbit_client.channel.basic_consume(
            queue=DataStorage.ITEM_QUEUE,
            on_message_callback=self._item_update_callback,
            auto_ack=True,
        )

    # ---------- Cart operations ---------- #
    def add_to_cart(self, user_id: int, item_id: int):
        cart_key = f"cart:{user_id}"
        self.redis_client.sadd(cart_key, str(item_id))

    def get_cart_items(self, user_id: int) -> list[Dict]:
        cart_key = f"cart:{user_id}"
        item_ids = self.redis_client.smembers(cart_key)
        items_in_cart = []
        if item_ids:
            pipeline = self.redis_client.pipeline()
            for item_id in item_ids:
                pipeline.get(f"item:{item_id}")
            results = pipeline.execute()
            items_in_cart = [json.loads(item) for item in results if item]
        return items_in_cart

    def is_item_in_cart(self, user_id: int, item_id: int) -> bool:
        """Checks if an item is in the user's cart."""
        cart_key = f"cart:{user_id}"
        return self.redis_client.sismember(cart_key, str(item_id))

    def remove_from_cart(self, user_id: int, item_id: int):
        """Removes item from cart in redis."""
        cart_key = f"cart:{user_id}"
        self.redis_client.srem(cart_key, str(item_id))

    def clear_cart(self, user_id: int):
        """Clear user cart in redis."""
        cart_key = f"cart:{user_id}"
        self.redis_client.delete(cart_key)

    # ---------- RabbitMQ operations ---------- #
    def _start_consuming_sync(self):
        try:
            self.rabbit_client.channel.start_consuming()
        except Exception as e:
            logger.error(f"An error occurred in Rabbit consumer: {e}")

    def _item_update_callback(self, ch, method, properties, body):
        """
        Callback function for handling item update messages from RabbitMQ.

        Parses incoming messages to determine if they are item update or
        item delete messages and dispatches them to the appropriate handlers.

        Args:
            ch: The Pika channel object.
            method: The Pika method frame.
            properties: The Pika message properties.
            body: The message body.

        Raises:
            json.JSONDecodeError: If the message body is not valid JSON.
            ValidationError: If the message content does not match
                `ItemDeleteMessage` or `ItemUpdateMessage` schema.
        """
        try:
            item = json.loads(body.decode())
            if item.get("channel") == "item_deletes":
                try:
                    item_delete_message = ItemDeleteMessage(**item)
                    asyncio.create_task(self.delete_item(item_delete_message.id))
                    logger.info(
                        f"Received request: delete item with id={item_delete_message.id}"
                    )
                except ValidationError as e:
                    logger.error(
                        f"Error validating item delete message: {e}. Message body: {body}"
                    )
                return

            try:
                item_update_message = ItemUpdateMessage(**item)
                asyncio.create_task(self.store_item(item_update_message.model_dump()))
                logger.info(
                    f"Received request: update item with id={item_update_message.id}"
                )

            except ValidationError as e:
                logger.error(
                    f"Error validating item update message: {e}. Message body: {body}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}. Message body: {body}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    @staticmethod
    async def calculate_total_pages(items: List[Dict]):
        """
        Calculates the total number of pages for items.
        """
        items_per_page = 3
        return (len(items) + items_per_page - 1) // items_per_page


data_storage = DataStorage()
