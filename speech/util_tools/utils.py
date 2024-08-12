# flake8: noqa
import os
import datetime
import logging

from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from pathlib import Path

from main_speech import main as speech_main
from threads import ThreadWithReturnValue
from chat import add_prompt
from constants import MY_CHAT_ID, bot
from db import UserAuth, Guest
from util_tools.file_handler import handle_file as file_handle
from util_tools.file_handler import final_file_write, handle_pdf


class Text(StatesGroup):
    text = State()


class File(StatesGroup):
    file = State()


class Feedback(StatesGroup):
    feedback = State()


class Premium(StatesGroup):
    duration = State()


class Voice(StatesGroup):
    voice = State()


class FileName(StatesGroup):
    name = State()


async def transcribe_audio_thread(name: str):
    thread = ThreadWithReturnValue(
        target=speech_main, args=(name,))
    thread.start()
    return thread.join()


async def handle_file(file: types.File, file_name: str, path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)

    await bot.download_file(
        file_path=file.file_path, destination=f"{path}/{file_name}"
    )


async def premium_requests(username, user_id, duration):
    kb = [
        types.InlineKeyboardButton(
            text=f"Выдать премиум {username}", callback_data='give_premium'),
        types.InlineKeyboardButton(
            text="В меню", callback_data='menu')
    ]
    keyboard = InlineKeyboardBuilder()

    keyboard.add(*kb)
    await bot.send_message(
        MY_CHAT_ID, f'Пользователь {
            username}, запросил премиум! {user_id}, {duration}',
        reply_markup=keyboard.adjust(1).as_markup()
    )


async def main_speech_func(message, name, msg):
    logging.info('main_speech_func started')
    if not name.endswith('.mp3'):
        ans = await speech_main(f"{name}.mp3")
        await bot.delete_message(message.chat.id, msg.message_id)
    else:
        ans = await speech_main(f'uploaded_files/{name}')
        await bot.delete_message(message.chat.id, msg.message_id)
        os.remove(f'uploaded_files/{name}')
    final_file = await final_file_write(ans, name)
    file = types.FSInputFile(final_file)
    button = types.InlineKeyboardButton(
        text='В меню', callback_data='menu')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)
    await bot.send_message(
        message.chat.id,
        f'Готово!\N{smiling face with sunglasses}\n\n'
        'Ниже - твой коснпект.',
    )
    await bot.send_document(
        message.chat.id, file, reply_markup=keyboard.adjust(
            1).as_markup()
    )
    os.remove(f"{name}_final.txt")


async def del_premium_request(username, user_id):
    kb = [
        types.InlineKeyboardButton(
            text='Забрать премиум', callback_data='del_premium'),
        types.InlineKeyboardButton(text="В админку", callback_data='admin'),
        types.InlineKeyboardButton(text="В меню", callback_data='menu')
    ]
    keyboard = InlineKeyboardBuilder()

    keyboard.add(*kb)
    await bot.send_message(
        MY_CHAT_ID, f'Забрать премиум у пользователя {username}, {user_id}??',
        reply_markup=keyboard.adjust(1).as_markup()
    )


def delete_premium(user_id):
    return UserAuth.get(
        UserAuth.user_id == user_id, UserAuth.premium == False
    )


def user_expiry_date(term):
    return datetime.datetime.now() + datetime.timedelta(days=30 * term)


def check_premium(user_id):
    user = UserAuth.get_or_none(
        UserAuth.user_id == user_id,
        UserAuth.premium == True
    )
    try:
        expiry = (user.expiry_date - datetime.datetime.now()).days
    except AttributeError:
        return None
    if expiry <= 0:
        user.premium = False

    if user is not None:
        return expiry
    return None


async def premium_limit(message):
    button = types.InlineKeyboardButton(
        text='Получить премиум', callback_data='getpremium')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)

    await message.answer(f'{message.from_user.first_name}, '
                         f'ты уже пробовал!\N{tired face}\n\n'
                         'Больше коспектов доступно с премиум подпиской.',
                         reply_markup=keyboard.adjust(1).as_markup())


async def bot_get_file(file_id, message):
    button = types.InlineKeyboardButton(
        text='Загрузил', callback_data='loaded')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)
    try:
        file = await bot.get_file(file_id)
        return file
    except TelegramBadRequest:
        await message.reply(
            f'Файл слишком большой.\n\n'
            'Пожалуйста, загрузи файл на сайт http://abstraction.ddns.net '
            'скопируй название файла и нажми кнопку "Загрузил".',
            reply_markup=keyboard.adjust(1).as_markup()
        )


async def file_prompt(message, user_id, name):
    if message.document is not None:
        file_id = message.document.file_id
        file = await bot_get_file(file_id, message)
        file_path = file.file_path

        Guest.update(made_speech=True).where(
            Guest.user_id == message.from_user.id).execute()
        logging.info(f'{name} requested file prompt')

        if file_path.endswith('.txt'):
            await file_handle(file, name, file_path, message)
        elif file_path.endswith('.pdf'):
            await handle_pdf(file, name, file_path, message)
        else:
            await message.answer('Неподдерживаемый тип файлов!')

    else:
        await message.answer('Можно отправлять только файлы!')


async def text_util(message, message_text):
    button = types.InlineKeyboardButton(
        text='В меню', callback_data='menu')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)
    ans = await add_prompt(message_text)
    await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())
