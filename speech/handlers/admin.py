# flake8: noqa
from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


from constants import MY_CHAT_ID, bot
from db import UserAuth
from util_tools.utils import (
    user_expiry_date,
    Voice,
)

router = Router()


@router.callback_query(F.data == 'admin')
async def admin(callback=types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id == MY_CHAT_ID:
        kb = [
            types.InlineKeyboardButton(
                text="Список премиум пользователей",
                callback_data='getpremiums'),

        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer(
            'Привет, админ! Вот тебе твои возможности',
            reply_markup=keyboard.adjust(2).as_markup()
        )
    else:
        await callback.answer("Ты не админ")


@router.callback_query(F.data == 'give_premium')
async def give_premium(callback: types.CallbackQuery):
    args = callback.message.text.replace('Пользователь ', '')
    args = args.replace(' запросил премиум!', '')
    username = args.split(', ')[0]
    user_id = int(args.split(', ')[1])
    duration = int(args.split(', ')[2])
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username,
        UserAuth.premium == True
    )

    if user is not None:
        await callback.message.answer('Такой пользователь уже есть!',
                                      show_alert=True)
    else:
        UserAuth.create(
            username=username,
            premium=True,
            user_id=int(user_id),
            expiry_date=user_expiry_date(duration)
        )

        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu')
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer(f'Премиум выдан!\N{green heart}',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      ))
        await bot.send_message(
            int(user_id), f'Вы получили премиум!\N{green heart}',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'del_premium')
async def del_premium(callback: types.CallbackQuery):

    args = callback.message.text.replace('Забрать премиум у пользователя ', '')
    args = args.replace('?', '')
    username = args.split(', ')[0]
    user_id = int(args.split(', ')[1])
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username)

    if user is None:
        await callback.message.answer('Такого пользователя нет!')
    else:
        UserAuth.delete().where(
            UserAuth.user_id == int(user_id),
            UserAuth.username == username
        ).execute()
        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu')
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer('Премиум удален!',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      ))
        await bot.send_message(int(user_id), f'У вас больше нет премиума!\N{broken heart}',
                               reply_markup=(
            keyboard.adjust(1).as_markup()
        ))
