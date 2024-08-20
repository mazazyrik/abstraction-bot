import logging
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import UserAuth
from constants import bot, MY_CHAT_ID
from util_tools.utils import (
    check_payment,
    premium_requests,
    Premium,
    premium_for_payment,
    user_expiry_date
)

router = Router()


@router.callback_query(F.data == 'getpremium')
async def get_premium(callback: types.CallbackQuery):
    if UserAuth.select().where(
            UserAuth.premium == True,
            UserAuth.user_id == callback.from_user.id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    else:

        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Оплатить', callback_data='pay'
            ),
            types.InlineKeyboardButton(
                text='Партнерская подписка', callback_data='paied'),
        )
        await callback.message.answer(
            f'Чтобы получить полный доступ - купи премиум.'
            f'\N{money-mouth face}\n'
            f'\nПрайс лист:\n'
            f'1 месяц = 299 рублей. \n'
            f'3 месяца = 800 рублей. \n'
            f'9 месяцев = 2500 рублей. \n'
            f'\nНажми "Оплатить" для оплаты.\n\n'
            f'Если ты партнер, нажми "Партнерская подписка".',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'paied')
async def paied(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Premium.duration)
    buttons = [
        [types.KeyboardButton(text='1 месяц')],
        [types.KeyboardButton(text='3 месяца')],
        [types.KeyboardButton(text='9 месяцев')]
    ]

    markup = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await callback.message.answer('Выбери длительность премиума', reply_markup=markup)


@router.callback_query(F.data == 'pay')
async def pay(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Premium.duration_for_payment)
    buttons = [
        [types.KeyboardButton(text='1 месяц')],
        [types.KeyboardButton(text='3 месяца')],
        [types.KeyboardButton(text='9 месяцев')]
    ]

    markup = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await callback.message.answer('Выбери длительность премиума', reply_markup=markup)


@router.message(Premium.duration_for_payment)
async def duration_for_payment_msg(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardBuilder()
    if message.text == '1 месяц':
        url, id = premium_for_payment(
            message.from_user.username, message.from_user.id, 1, message)
    elif message.text == '3 месяца':
        url, id = premium_for_payment(
            message.from_user.username, message.from_user.id, 3, message)
    elif message.text == '9 месяцев':
        url, id = premium_for_payment(
            message.from_user.username, message.from_user.id, 9, message)
    keyboard.add(
        types.InlineKeyboardButton(
            text='Оплатить', url=url
        ),
        types.InlineKeyboardButton(
            text='Оплатил', callback_data=f'yookassa_{id}'
        ),
    )
    msg = await message.answer(
        'Формирование ссылки на оплату...',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await bot.delete_message(message.chat.id, msg.message_id)
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer(
        'После оплаты нажмите вернуться в магазин и нажмите "Оплатил"',
        reply_markup=keyboard.adjust(1).as_markup()
    )


@router.callback_query(lambda c: 'yookassa' in c.data)
async def yookassa(callback: types.CallbackQuery):
    id = callback.data.split('_')[-1]
    payment = check_payment(id)

    if payment.status == 'succeeded':
        username = payment.metadata['username']
        user_id = payment.metadata['user_id']
        term = payment.metadata['term']
        user = UserAuth.get_or_none(
            UserAuth.user_id == int(user_id),
            UserAuth.username == username,
            UserAuth.premium == True
        )
        if user is not None:
            user.expiry_date = user_expiry_date(int(term))
        else:
            UserAuth.create(
                username=username,
                premium=True,
                user_id=int(user_id),
                expiry_date=user_expiry_date(term)
            )

        await callback.message.answer(
            f'Спасибо за оплату!\n'
            'Если премиум не будет выдан после оплаты \N{unamused face} свяжитесь с @abstractionsupport',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            MY_CHAT_ID, f'Премиум выдан {username}, {user_id}, {term}')
    else:
        logging.error(payment)
        await callback.message.answer(
            f'Оплата не прошла!\n'
            'Если премиум не будет выдан после оплаты \N{unamused face} свяжитесь с @abstractionsupport',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            MY_CHAT_ID, f'Оплата не прошла {payment.id}, {payment.status}')


@router.message(Premium.duration)
async def duration_msg(message: types.Message, state: FSMContext):
    await state.clear()
    if message.text == '1 месяц':
        await premium_requests(message.from_user.username, message.from_user.id, 1)
    elif message.text == '3 месяца':
        await premium_requests(message.from_user.username, message.from_user.id, 3)
    elif message.text == '9 месяцев':
        await premium_requests(message.from_user.username, message.from_user.id, 9)
    await message.answer(
        f'Ожидайте, пока оператор проверит вашу заявку!\n\n'
        f'Если оператор не отвечает в течении часа \N{unamused face} свяжитесь с @abstractionsupport',
        reply_markup=types.ReplyKeyboardRemove()
    )
