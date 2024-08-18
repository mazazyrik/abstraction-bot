# flake8: noqa
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Guest, UserAuth
from chat import add_prompt
from util_tools.utils import (
    Text, premium_limit, premium_requests, del_premium_request, File, Feedback,
    Premium, check_premium, file_prompt, text_util, premium_for_payment, user_expiry_date
)
from constants import MY_CHAT_ID, bot

router = Router()


@router.callback_query(F.data == 'checkpremium')
async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    check = check_premium(user_id)
    if check is None:
        await callback.message.answer(f'У вас нет премиума!\N{broken heart}')

    else:
        await callback.message.answer(f'У вас есть премиум! Осталось: {check} дней.')


@router.callback_query(F.data == 'text')
async def text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Text.text)
    await callback.message.answer('Напиши текст для создания коспекта.')


@router.message(Text.text)
async def text_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    check_premium(user_id)
    await state.clear()
    message_text = message.text
    if UserAuth.select().where(
        UserAuth.user_id == user_id, UserAuth.premium == True
    ):
        await text_util(message, message_text)
    elif (
        Guest.select().where(
            Guest.user_id == user_id, Guest.made_speech == True
        ).exists() or UserAuth.select().where(
            UserAuth.user_id == user_id, UserAuth.premium == False
        )
    ):
        await premium_limit(message)

    elif (
        Guest.select().where(
            Guest.user_id == user_id, Guest.made_speech == False
        ).exists()
    ):
        await text_util(message, message_text)
        Guest.update(made_speech=True).where(
            Guest.user_id == message.from_user.id).execute()
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=message.from_user.username)
        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        ans = await add_prompt(message_text)
        await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())
        Guest.update(made_speech=True).where(
            Guest.user_id == message.from_user.id).execute()


@router.callback_query(F.data == 'text_file')
async def text_file(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(File.file)
    await callback.message.answer(
        f'Отправь мне файл для создания коспекта.\n\n'
        'Файлы принимаются только с расширениями .txt и .pdf'
    )


@router.message(File.file, F.content_type.in_({'document'}))
async def text_file_msg(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    check_premium(user_id)
    name = message.from_user.username
    if UserAuth.select().where(
        UserAuth.user_id == user_id, UserAuth.premium == True
    ):
        await file_prompt(message, user_id, name)
    elif (
        Guest.select().where(
            Guest.user_id == user_id, Guest.made_speech == True
        ).exists() or UserAuth.select().where(
            UserAuth.user_id == user_id, UserAuth.premium == False
        ).exists()
    ):
        await premium_limit(message)
    elif Guest.select().where(
        Guest.user_id == user_id, Guest.made_speech == False
    ).exists():
        await file_prompt(message, user_id, name)
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=message.from_user.username)
        await file_prompt(message, user_id, name)


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


@router.callback_query(F.data == 'getpremiums')
async def get_premiums(callback: types.CallbackQuery):
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    if list(premium_users) == []:
        await callback.message.answer('Никто не имеет премиума!')
    for user in premium_users:
        await del_premium_request(user.username, int(user.user_id))


@router.callback_query(F.data == 'feedback')
async def feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Feedback.feedback)
    await callback.message.answer(
        f'Напиши свои пожелания и предложения \N{thinking face}'
    )


@ router.message(Feedback.feedback)
async def feedback_msg(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        f'Отзыв от {message.from_user.username}:\n'
        f'{message.text}'
    )
    await bot.send_message(MY_CHAT_ID, text)
    await message.answer(f'Спасибо за ваш отзыв!\N{green heart}')
