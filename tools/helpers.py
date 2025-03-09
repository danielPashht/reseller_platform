import random


def generate_items(num_items=10):
    items = []
    for i in range(num_items):
        item = {
            "name": f"Item {i+1}",
            "description": f"Description for item {i+1}",
            "price": round(random.uniform(10.0, 100.0), 2)
        }
        items.append(item)
    return items
