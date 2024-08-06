# flake8: noqa
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Guest, UserAuth
from chat import add_prompt
from util_tools.utils import (
    Text, premium_requests, del_premium_request, File, Feedback,
    Premium, check_premium
)
from util_tools.file_handler import handle_file
from constants import MY_CHAT_ID, bot

router = Router()


@router.callback_query(F.data == 'checkpremium')
async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    check = check_premium(user_id)
    if check is None:
        await callback.message.answer('У вас нет премиума!')

    else:
        await callback.message.answer(f'У вас есть премиум! Осталось: {check} дней.')


@router.callback_query(F.data == 'text')
async def text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Text.text)
    await callback.message.answer('Напиши текст для создания коспекта')


@router.message(Text.text)
async def text_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    check_premium(user_id)
    await state.clear()
    message_text = message.text
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


@router.callback_query(F.data == 'text_file')
async def text_file(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(File.file)
    await callback.message.answer('Отправь мне файл для создания коспекта')


@router.message(File.file, F.content_type.in_({'document'}))
async def text_file_msg(message: types.Message, state: FSMContext):
    await state.clear()
    name = message.from_user.username
    if message.document is not None:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await handle_file(file, name, file_path, message)


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
                text='Оплатил', callback_data='paied'),
        )
        await callback.message.answer(
            f'Чтобы получить полный доступ - купи премиум.'
            f'\N{money-mouth face}\n'
            f'\nПрайс лист:\n'
            f'1 месяц = 600 рублей. \n'
            f'3 месяца = 1500 рублей. \n'
            f'9 месяцев = 5100 рублей. \n'
            f'\nПереводи по ссылке с коментарием'
            f' "Премиум".\n'
            f'Ссылка:\n'
            'https://www.tinkoff.ru/rm/chuvaev.nikita7/6cJIt194'
            f'\n\n После оплаты нажми кнопку "Оплатил" и выбери длительность премиума.',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'paied')
async def paied(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Premium.duration)
    kb = [
        [types.KeyboardButton(text='1')],
        [types.KeyboardButton(text='3')],
        [types.KeyboardButton(text='9')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await callback.message.answer('Выбери длительность премиума', reply_markup=keyboard)


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
        'Ожидайте, пока оператор проверит вашу заявку!',
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
    await callback.message.answer('Напиши свои пожелания и предложения')


@router.message(Feedback.feedback)
async def feedback_msg(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        f'Отзыв от {message.from_user.username}:\n'
        f'{message.text}'
    )
    await bot.send_message(MY_CHAT_ID, text)
    await message.answer('Спасибо за ваш отзыв!')
