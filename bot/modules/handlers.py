from dataclasses import dataclass
import json
import httpx
from bot import config
from pydantic import ValidationError
from logging import getLogger
from bot.db.schemas import Order
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery


from bot.modules.keyboards import (
    main_menu_kb,
    contacts_inline_kb,
    get_catalog_keyboard,
    get_item_details_keyboard,
    get_cart_keyboard,
)

ITEMS_PER_PAGE = 3
current_page = 0

logger = getLogger("bot")


@dataclass
class CustomFilters:
    CONTACTS = "Контакты"
    CATALOG = "Каталог"
    CART = "Корзина"


def create_router(data_storage, bot: Bot):
    """
    Creates and configures the router for the Telegram bot.

    Args:
        data_storage: An instance of DataStorage for interacting with item data.
        bot: The aiogram Bot instance.
        manager_chat_id: The chat ID of the manager to receive order notifications.
    Returns:
        The configured aiogram Router.
    """
    router = Router()

    async def _notify_manager(bot: Bot, username: str = None, order_id: int = None):
        """Sends a notification to the manager about a new order."""
        try:
            order_info_text = (
                f"🔔 Новый заказ!\n\n"
                f"- Пользователь: {f'@{username}' if username else 'Не указан'}\n"
                f"- Номер заказа: {order_id if order_id else 'Не указан'}"
            )
            await bot.send_message(chat_id=config.MANAGER_USER_ID, text=order_info_text)
            logger.info(
                f"Successfully sent order notification to manager (user_id: {config.MANAGER_USER_ID})"
            )
        except Exception as e:
            logger.error(f"Failed to send order notification to manager: {e}")

    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            text=f"👋 Приветствуем в Design Studio, {message.from_user.full_name}!",
            reply_markup=main_menu_kb,
        )

    @router.message(F.text == CustomFilters.CART)
    async def cmd_view_cart(message: Message):
        user_id = message.from_user.id
        cart_items = data_storage.get_cart_items(user_id)

        if not cart_items:
            await message.answer(
                "Ваша корзина пуста. 🛒 Добавьте товары из каталога",
                reply_markup=get_catalog_keyboard(
                    0, items=await data_storage.get_all_items()
                ),
            )
            return
        else:
            cart_item_names = [
                f"- {item['name']} (Цена: {item['price']})" for item in cart_items
            ]
            cart_text = "🛒 Ваша корзина:\n" + "\n".join(cart_item_names)
            await message.answer(cart_text, reply_markup=get_cart_keyboard(user_id))

    @router.message(F.text == CustomFilters.CONTACTS)
    async def cmd_contacts(message: Message):
        await message.answer("Наши контакты", reply_markup=contacts_inline_kb)

    @router.message(F.text == CustomFilters.CATALOG)
    async def cmd_catalog(message: Message):
        global current_page
        current_page = 0
        items = await data_storage.get_all_items()
        keyboard = get_catalog_keyboard(current_page, items=items)
        total_pages = await data_storage._calculate_total_pages(items)
        catalog_message_text = (
            f"🌟 Наши услуги 🌟\n\n"
            "Выберите услугу или используйте кнопки для навигации.\n\n"
            f"Страница {current_page + 1} из {total_pages}"
        )
        await message.answer(catalog_message_text, reply_markup=keyboard)

    @router.callback_query(F.data.startswith("item_"))
    async def view_item_details(callback_query: CallbackQuery):
        item_id = int(callback_query.data.split("_")[1])
        item_key = f"item:{item_id}"
        item = data_storage.redis_client.get(item_key)
        item = json.loads(item)
        user_id = callback_query.from_user.id
        keyboard = get_item_details_keyboard(item_id=item_id, user_id=user_id)
        await callback_query.message.answer(
            f"📋 {item['name']}\n"
            f"💰 Цена: от {item['price']}\n"
            f"📝 Описание: {item['description']}",
            reply_markup=keyboard,
        )

    @router.callback_query(F.data.in_(["next_page", "prev_page", "back_to_catalog"]))
    async def handle_navigation(callback_query: CallbackQuery):
        global current_page
        if callback_query.data == "next_page":
            current_page += 1
        elif callback_query.data == "prev_page":
            current_page -= 1
        elif callback_query.data == "back_to_catalog":
            current_page = 0  # Return to first page
        items = await data_storage.get_all_items()
        keyboard = get_catalog_keyboard(current_page, items=items)
        total_pages = await data_storage._calculate_total_pages(items)
        catalog_text = (
            f"🌟 Каталог услуг 🌟\n\n(Страница {current_page + 1} из {total_pages})"
        )
        await callback_query.message.edit_text(catalog_text, reply_markup=keyboard)

    @router.callback_query(F.data.startswith("add_to_cart_"))
    async def add_to_cart(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        item_id = int(callback_query.data.split("_")[-1])

        if data_storage.is_item_in_cart(user_id, item_id):
            await callback_query.answer("⚠️ Уже в корзине")

        data_storage.add_to_cart(user_id, item_id)
        await callback_query.answer("✅ Добавлено в корзину")

    @router.callback_query(F.data.startswith("clear_cart"))
    async def clear_cart(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        data_storage.clear_cart(user_id)
        await callback_query.answer("Корзина очищена 👌")

    @router.callback_query(F.data.startswith("checkout"))
    async def send_order(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        cart_items: list[dict] = data_storage.get_cart_items(user_id)

        if not cart_items:
            await callback_query.answer("Ваша корзина пуста!", show_alert=True)
            return

        order_items_details = []
        total_price = 0
        for item in cart_items:
            order_items_details.append({"name": item["name"], "price": item["price"]})
            total_price += float(item["price"])

        order_data = {
            "user_id": user_id,
            "username": callback_query.from_user.username,
            "order_items": cart_items,
            "total_price": total_price,
        }

        await _validate_order(order_data)

        try:
            order_id = await _post_order(order_data)
        except Exception as exc:
            logger.error(f"Failed to process order: {exc}")
            await callback_query.answer(
                "Произошла ошибка при оформлении заказа. Попробуйте позже.",
                show_alert=True,
            )
            return

        data_storage.clear_cart(user_id=user_id)

        order_text = "📦 Ваш заказ принят!\n\n"
        for item_detail in order_items_details:
            order_text += f"- {item_detail['name']} ({item_detail['price']})\n"
        order_text += f"\nИтого: ${total_price}"

        await _notify_manager(
            bot, username=callback_query.from_user.username, order_id=order_id
        )

        await callback_query.message.answer(order_text)
        await callback_query.answer(
            text="Заказ принят в работу 👌 Менеджер свяжется с вами в ближайшее время",
            show_alert=True,
        )

    async def _post_order(order_data: dict) -> int | None:
        """Posts the order data to the backend API and returns the order_id."""
        headers = {"X-API-Key": config.ADMIN_API_KEY}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{config.ADMIN_API_URL}/order/", json=order_data, headers=headers
                )
                response.raise_for_status()

                try:
                    response_data = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON response: {e}")
                    raise Exception("Failed to decode JSON response")

                order_id = response_data.get("order_id")
                if order_id is None:
                    logger.error("order_id not found in response")
                    raise Exception("order_id not found in response")

                logger.info(f"POST request to /order/ successful. Order ID: {order_id}")
                return order_id

            except httpx.HTTPError as e:
                logger.error(f"Error in POST request to /order/: {e}")
                raise

    async def _validate_order(order_data: dict) -> bool:
        user_id = order_data.get("user_id")
        cart_items = order_data.get("order_items")
        total_price = order_data.get("total_price")
        username = order_data.get("username")

        try:
            Order(user_id=user_id, items=cart_items, total_price=total_price, username=username)
        except ValidationError as exc:
            logger.error(f"Order validation failed: {exc}")
            raise exc

    return router
