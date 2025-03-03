import json
from typing import Any
from config import rabbit_channel

from sqladmin import ModelView
from starlette.requests import Request

from models import ItemModel, OrderModel


class OrderAdmin(ModelView, model=OrderModel):
	is_async = True
	name_plural = "Orders"
	can_edit = False
	can_create = False
	can_delete = False
	column_list = [OrderModel.id, OrderModel.username, OrderModel.user_telegram_id, OrderModel.total, OrderModel.status]
	column_searchable_list = [OrderModel.username, OrderModel.user_telegram_id]
	column_filters = [OrderModel.status]


class ItemAdmin(ModelView, model=ItemModel):
	is_async = True
	name_plural = "Items"
	column_list = [ItemModel.id, ItemModel.name, ItemModel.description, ItemModel.price]
	column_searchable_list = [ItemModel.name]
	column_filters = [ItemModel.name]

	async def after_model_change(
			self, data: dict, model: Any,
			is_created: bool, request: Request) -> None:
		""" Publish item updates to RabbitMQ """
		message = {
			'id': model.id,
			'name': model.name,
			'description': model.description,
			'price': model.price
		}
		rabbit_channel.basic_publish(
			exchange='reseller_exchange',
			routing_key='item_updates',
			body=json.dumps(message)
		)
