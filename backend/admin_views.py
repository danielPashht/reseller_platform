from sqladmin import ModelView
from models import ItemModel, OrderModel


# ----------------- Admin views ----------------- #
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
