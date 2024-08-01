# flake8: noqa
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from db import Guest, UserAuth
from chat import add_prompt
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from utils import Text, premium_requests, del_premium_request, main_speech_func

MY_CHAT_ID = 387435447


bot = Bot(token="7149556054:AAFPIKcoj97DvflYdaCVlFtbNRJb4QKb87I")
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


@dp.callback_query(F.data == 'checkpremium')
async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if UserAuth.select().where(UserAuth.user_id == user_id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    else:
        await callback.message.answer('У вас нет премиум аккаунта!')


@dp.callback_query(F.data == 'text')
async def text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Text.text)
    await callback.message.answer('Напиши текст для создания коспекта')


@dp.message(Text.text)
async def text_msg(message: types.Message, state: FSMContext):
    await state.clear()
    message_text = message.text
    user_id = message.from_user.id
    if Guest.select().where(Guest.user_id == user_id, Guest.made_speech == True).exists():

        button = types.InlineKeyboardButton(
            text='Получить премиум', callback_data='getpremium')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)

        await message.answer('Ты уже пробовал! '
                             'Больше коспектов доступно с премиум подпиской.',
                             reply_markup=keyboard.adjust(1).as_markup())
    elif Guest.select().where(Guest.user_id == user_id, Guest.made_speech == False).exists():
        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        ans = await add_prompt(message_text)
        await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=message.from_user .username)
        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        ans = await add_prompt(message_text)
        await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())


@dp.callback_query(F.data == 'getpremium')
async def get_premium(callback: types.CallbackQuery):
    username = callback.from_user.username
    user_id = callback.from_user.id

    await callback.message.answer(
        'Чтобы получить полный доступ - купи премиум. '
        '1 месяц = 600 рублей. '
        'Переводи через СБП на Тинькофф по номеру 89771416389 с коментарием'
        ' "Премиум".'
        ' Либо по ссылке '
        'https://www.tinkoff.ru/rm/chuvaev.nikita7/6cJIt194'
    )

    await premium_requests(username, user_id)


@dp.callback_query(F.data == 'getpremiums')
async def get_premiums(callback: types.CallbackQuery):
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    if list(premium_users) == []:
        await callback.message.answer('Никто не имеет премиума!')
    for user in premium_users:
        await del_premium_request(user.username, int(user.user_id))


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
