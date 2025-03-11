import json
from decimal import Decimal


def generate_items():
    with open('items.json', 'r') as file:
        items_data = json.load(file)

    items = []
    for item_data in items_data:
        item = {
            "name": item_data.get("name", ""),
            "description": item_data.get("description", ""),
            "price": item_data.get("price", 0.0)
        }
        items.append(item)

    return items


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
