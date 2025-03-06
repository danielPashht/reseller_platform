import json
from typing import Any
from config import rabbit_channel
from models import ItemModel, OrderModel
from main import admin

from sqladmin import ModelView
from starlette.requests import Request


class OrderAdmin(ModelView, model=OrderModel):
	is_async = True
	name_plural = "Orders"
	can_edit = False
	can_create = False
	can_delete = False
	column_list = [OrderModel.id, OrderModel.user_id, OrderModel.total_price, OrderModel.status]
	column_searchable_list = [OrderModel.user_id]
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

	async def after_model_delete(
			self, model: Any, request: Request) -> None:
		""" Publish item deletion to RabbitMQ """
		message = {
			'id': model.id,
			'name': model.name,
			'description': model.description,
			'price': model.price,
			'deleted': True
		}

		rabbit_channel.basic_publish(
			exchange='reseller_exchange',
			routing_key='item_deletes',
			body=json.dumps(message)
		)


admin.add_view(ItemAdmin)
admin.add_view(OrderAdmin)
