import logging
import asyncio

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram import types, F
from aiogram.fsm.context import FSMContext


from constants import bot
from state import Text
from service_funcs import (
    cmd_start,
    cmd_try,
    menu,
    voice_message_handler,
    admin, give_premium,
    del_premium
)
from main_bot import (
    checkpremium,
    text,
    text_msg,
    get_premium,
    get_premiums
)

logging.basicConfig(level=logging.INFO)


dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start_main(message: types.Message):
    await cmd_start(message)


@dp.callback_query(F.data == 'menu')
async def menu_main(callback: types.CallbackQuery):
    await menu(callback)


@dp.callback_query(F.data == 'try')
async def cmd_try_main(callback: types.CallbackQuery):
    await cmd_try(callback)


@dp.message(F.content_type.in_({'audio', 'voice'}))
async def voice_message_handler_main(message: types.Message):
    await voice_message_handler(message)


@dp.callback_query(F.data == 'admin')
async def admin_main(callback=types.CallbackQuery):
    await admin(callback)


@dp.callback_query(F.data == 'give_premium')
async def give_premium_main(callback: types.CallbackQuery):
    await give_premium(callback)


@dp.callback_query(F.data == 'del_premium')
async def del_premium_main(callback: types.CallbackQuery):
    await del_premium(callback)


@dp.callback_query(F.data == 'checkpremium')
async def checkpremium_main(callback: types.CallbackQuery):
    await checkpremium(callback)


@dp.callback_query(F.data == 'text')
async def text_main(callback: types.CallbackQuery, state: FSMContext):
    await text(callback, state)


@dp.message(Text.text)
async def text_msg_main(message: types.Message, state: FSMContext):
    await text_msg(message, state)


@dp.callback_query(F.data == 'getpremium')
async def get_premium_main(callback: types.CallbackQuery):
    await get_premium(callback)


@dp.callback_query(F.data == 'getpremiums')
async def get_premiums_main(callback: types.CallbackQuery):
    await get_premiums(callback)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
