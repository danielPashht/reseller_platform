from sqladmin import ModelView
from models import Item, Order


# ----------------- Admin views ----------------- #
class OrderAdmin(ModelView, model=Order):
	is_async = True
	name_plural = "Orders"
	can_edit = False
	can_create = False
	can_delete = False
	column_list = [Order.id, Order.username, Order.user_telegram_id, Order.total, Order.status]
	column_searchable_list = [Order.username, Order.user_telegram_id]
	column_filters = [Order.status]


class ItemAdmin(ModelView, model=Item):
	is_async = True
	name_plural = "Items"
	column_list = [Item.id, Item.name, Item.description, Item.price]
	column_searchable_list = [Item.name]
	column_filters = [Item.name]
