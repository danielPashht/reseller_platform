from typing import Dict
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина")],
        [KeyboardButton(text="Контакты")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an option",
)


contacts_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="GitHub", url="https://github.com/danielPashht")]
    ]
)


def get_catalog_keyboard(
    page: int, items: list[Dict], items_per_page: int = 3
) -> InlineKeyboardMarkup:
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    keyboard = []

    # Add item buttons for the current page
    start_idx = page * items_per_page
    end_idx = min((page + 1) * items_per_page, len(items))
    for item in items[start_idx:end_idx]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{item['name']} - ${item['price']}",
                    callback_data=f"item_{item['id']}",
                )
            ]
        )

    # Add navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Предыдущая", callback_data="prev_page")
        )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="Следующая ➡️", callback_data="next_page")
        )
    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_item_details_keyboard(item_id: int, user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 В корзину", callback_data=f"add_to_cart_{item_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад к каталогу", callback_data="back_to_catalog"
                )
            ],
        ]
    )


def get_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Оформить заказ", callback_data="checkout")],
            [
                InlineKeyboardButton(
                    text="🗑 Очистить корзину", callback_data="clear_cart}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Вернуться к каталогу", callback_data="back_to_catalog"
                )
            ],
        ]
    )
