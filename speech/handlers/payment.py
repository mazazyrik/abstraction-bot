from constants import bot
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import UserAuth
from util_tools.utils import (
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
                text='Оплата запросом', callback_data='paied'),
        )
        await callback.message.answer(
            f'Чтобы получить полный доступ - купи премиум.'
            f'\N{money-mouth face}\n'
            f'\nПрайс лист:\n'
            f'1 месяц = 299 рублей. \n'
            f'3 месяца = 800 рублей. \n'
            f'9 месяцев = 2500 рублей. \n'
            f'\nНажми "Оплатить" для оплаты в приложении.\n\n'
            f'Если оплата не проходит, то нажми "Оплата запросом"',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'paied')
async def paied(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Premium.duration)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('1', '3', '9')
    await callback.message.answer('Выбери длительность премиума', reply_markup=markup)


@router.callback_query(F.data == 'pay')
async def pay(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Premium.duration_for_payment)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('1', '3', '9')
    await callback.message.answer('Выбери длительность премиума', reply_markup=markup)


@router.message(Premium.duration_for_payment)
async def duration_for_payment_msg(message: types.Message, state: FSMContext):
    await state.clear()
    if message.text == '1':
        await premium_for_payment(message.from_user.username, message.from_user.id, 1, message)
    elif message.text == '3':
        await premium_for_payment(message.from_user.username, message.from_user.id, 3, message)
    elif message.text == '9':
        await premium_for_payment(message.from_user.username, message.from_user.id, 9, message)
    await message.answer(
        f'Если премиум не будет выдан после оплаты \N{unamused face} свяжитесь с @abstractionsupport',
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.shipping_query()
async def process_shipping_query(shipping_query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query.id, ok=True)


@router.message(lambda message: message.successful_payment)
async def successful_payment_handler(message: types.Message):
    if message.successful_payment:
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
            'Если премиум не будет выдан после оплаты \N{unamused face} свяжитесь с @abstractionsupport',
            reply_markup=types.ReplyKeyboardRemove()
        )


@router.message(Premium.duration)
async def duration_msg(message: types.Message, state: FSMContext):
    await state.clear()
    if message.text == '1':
        await premium_requests(message.from_user.username, message.from_user.id, 1)
    elif message.text == '3':
        await premium_requests(message.from_user.username, message.from_user.id, 3)
    elif message.text == '9':
        await premium_requests(message.from_user.username, message.from_user.id, 9)
    await message.answer(
        f'Ожидайте, пока оператор проверит вашу заявку!\n\n'
        f'Если оператор не отвечает в течении часа \N{unamused face} свяжитесь с @abstractionsupport',
        reply_markup=types.ReplyKeyboardRemove()
    )
