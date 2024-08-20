# flake8: noqa
import os
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Guest, UserAuth
from ogg_to_mp3 import to_mp3

from chat import add_prompt
from util_tools.utils import (
    Text, premium_limit, Feedback, main_speech_func,
    check_premium, text_util, bot_get_file, Voice
)
from constants import MY_CHAT_ID, bot

router = Router()


@router.callback_query(F.data == 'voice')
async def voice(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Voice.voice)
    await callback.message.answer(
        f'Отправь голосовое сообщение или мп3 файл.\n\n'
        'Если у тебя айфон, то ты можешь '
        'поделиться записью с диктофона и отправить боту.'
    )

@router.message(Voice.voice, F.content_type.in_({'audio', 'voice'}))
async def voice_message_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    check_premium(user_id)
    name = message.from_user.username
    premium_users = [user.username for user in UserAuth.select().where(
        UserAuth.premium == True)]
    aval_guests = [guest.username for guest in Guest.select().where(
        Guest.made_speech == False)]
    if name in (premium_users or aval_guests):
        if message.audio is not None:
            file_id = message.audio.file_id
            file = await bot_get_file(file_id, message)
            if file is not None:
                file_path = file.file_path
                try:
                    await bot.download_file(file_path, f"{name}.mp3")
                    msg = await message.reply("Загрузка...")
                    await main_speech_func(message, name, msg)
                    os.remove(f"{name}.mp3")
                except FileExistsError:
                    await message.reply(
                        "Вы не можете отправить новый запрос, "
                        "пока не закончите предыдущий!"
                    )

        else:
            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path

            msg = await message.reply("Загрузка...")
            try:
                await bot.download_file(file_path, f"{name}.ogg")
                to_mp3(f"{name}.ogg")
                await main_speech_func(message, name, msg)
                os.remove(f"{name}.ogg")
                os.remove(f"{name}.mp3")

                if name in aval_guests:
                    Guest.update(made_speech=True).where(
                        Guest.user_id == message.from_user.id).execute()
            except FileExistsError:
                await message.reply(
                    "Вы не можете отправить новый запрос, "
                    "пока не закончите предыдущий!"
                )

    else:
        kb = [
            types.InlineKeyboardButton(
                text='Получить премиум', callback_data='getpremium'),
            types.InlineKeyboardButton(
                text="Попробовать", callback_data='try'),
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await message.answer(
            f'У вас нет премиума! Что бы получить премиум, нажми "Получить премиум"!\n\n'
            'Если ты не пробовал, то нажми попробовать!',
            reply_markup=keyboard.adjust(1).as_markup()
        )


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
