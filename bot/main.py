import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from bot.modules.middlewares import BotMiddleware
from bot.db.storage import data_storage
from bot.modules.handlers import create_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")


async def main():
    from bot.config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)
    storage: MemoryStorage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.callback_query.middleware(CallbackAnswerMiddleware())
    router = create_router(data_storage, bot=bot)
    router.message.middleware(BotMiddleware(bot))
    router.callback_query.middleware(BotMiddleware(bot))
    dp.include_router(router)

    async def on_startup(dispatcher):
        """
        runs right before polling start
        """
        await data_storage.fetch_items()
        logging.info("Bot started")

    async def on_shutdown(dispatcher):
        logging.warning("Shutting down..")
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()
        logging.warning("Bye!")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
