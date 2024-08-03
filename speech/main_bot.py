# flake8: noqa
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Guest, UserAuth
from chat import add_prompt
from utils import premium_requests, del_premium_request
from state import Text
from constants import bot


async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if UserAuth.select().where(UserAuth.user_id == user_id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    else:
        await callback.message.answer('У вас нет премиум аккаунта!')


async def text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Text.text)
    await callback.message.answer(
        'Напиши текст для создания коспекта либо отправь файл с расширением .txt'
    )


async def text_msg(message: types.Message, state: FSMContext):
    await state.clear()
    username  = message.from_user.username
    if message.content_type == 'document':
        file = await bot.get_file(message.document.file_id, f'{username}.txt')
        file_path = file.file_path
        logging.info(file_path)
    else:

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


async def get_premiums(callback: types.CallbackQuery):
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    if list(premium_users) == []:
        await callback.message.answer('Никто не имеет премиума!')
    for user in premium_users:
        await del_premium_request(user.username, int(user.user_id))
