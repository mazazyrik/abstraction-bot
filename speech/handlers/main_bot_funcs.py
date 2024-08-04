# flake8: noqa
import os
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Guest, UserAuth
from chat import add_prompt
from util_tools.utils import (
    Text, premium_requests, del_premium_request, File, Feedback
)
from constants import MY_CHAT_ID, bot

router = Router()


@router.callback_query(F.data == 'checkpremium')
async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if UserAuth.select().where(UserAuth.user_id == user_id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    else:
        await callback.message.answer('У вас нет премиум аккаунта!')


@router.callback_query(F.data == 'text')
async def text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Text.text)
    await callback.message.answer('Напиши текст для создания коспекта')


@router.message(Text.text)
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
        try:
            await bot.download_file(file_path, f"{name}.txt")
            msg = await message.reply("Загрузка...")
            f = open(f'{name}.txt', 'r')
            text = f.read()
            button = types.InlineKeyboardButton(
                text='В меню', callback_data='menu')
            keyboard = InlineKeyboardBuilder()
            keyboard.add(button)
            final_text = await add_prompt(text)
            await bot.delete_message(message.chat.id, msg.message_id)
            ff = open(f'{name}_final.txt', 'w')
            ff.write(final_text)
            file = types.FSInputFile(f'{name}_final.txt')
            await bot.send_document(
                message.chat.id, file, reply_markup=keyboard.adjust(
                    1).as_markup()
            )
            os.remove(f"{name}.txt")
            os.remove(f"{name}_final.txt")
        except FileExistsError:
            await message.reply(
                "Вы не можете отправить новый запрос, "
                "пока не закончите предыдущий!"
            )


@router.callback_query(F.data == 'getpremium')
async def get_premium(callback: types.CallbackQuery):
    if UserAuth.select().where(
            UserAuth.premium == True,
            UserAuth.user_id == callback.from_user.id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    else:
        username = callback.from_user.username
        user_id = callback.from_user.id

        await callback.message.answer(
            f'Чтобы получить полный доступ - купи премиум.'
            f'\N{money-mouth face}\n'
            f'\nПрайс лист:\n'
            f'1 месяц = 600 рублей. \n'
            f'3 месяца = 1500 рублей. \n'
            f'9 месяцев = 5100 рублей. \n'
            f'\nПереводи через СБП на Тинькофф по номеру 89771416389 с коментарием'
            f' "Премиум".\n'
            f'Либо по ссылке:\n'
            'https://www.tinkoff.ru/rm/chuvaev.nikita7/6cJIt194'
        )

        await premium_requests(username, user_id)


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
