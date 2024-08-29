import asyncio
import logging

from aiogram import Dispatcher
from constants import bot as my_bot

from handlers import (
    main_bot_funcs, service_funcs, admin, payment, premium, file_handlers
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Specify the date format
)


async def main():
    bot = my_bot
    dp = Dispatcher()
    dp.include_routers(
        main_bot_funcs.router, service_funcs.router, admin.router,
        payment.router, premium.router, file_handlers.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    asyncio.run(main())
