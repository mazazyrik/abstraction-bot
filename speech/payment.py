from bot import dp
from constants import bot
from aiogram import types
from aiogram.enums.content_type import ContentType
from db import UserAuth
from util_tools.utils import user_expiry_date


@dp.pre_checkout_query_handler(func=lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    payload = message.successful_payment.to_python()['invoice_payload']
    parts = payload.split('_')

    username = parts[0]
    term = parts[3]
    user_id = parts[4]

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

    await bot.send_message(
        message.chat.id,
        f'Спасибо за оплату!\n'
        'Если премиум не будет выдан после оплаты \N{unamused face} свяжитесь с @abstraction.support',
        reply_markup=types.ReplyKeyboardRemove()
    )
