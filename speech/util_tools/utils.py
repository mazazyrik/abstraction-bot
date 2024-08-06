import datetime
import logging

from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path

from main_speech import main as speech_main
from threads import ThreadWithReturnValue
from chat import add_prompt
from constants import MY_CHAT_ID, bot
from db import UserAuth, Guest
from util_tools.file_handler import handle_file as file_handle


class Text(StatesGroup):
    text = State()


class File(StatesGroup):
    file = State()


class Feedback(StatesGroup):
    feedback = State()


class Premium(StatesGroup):
    duration = State()


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
    ans = await speech_main(f"{name}.mp3")
    button = types.InlineKeyboardButton(
        text='В меню', callback_data='menu')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)
    await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())
    await bot.delete_message(message.chat.id, msg.message_id)


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


async def file_prompt(message, user_id, name):
    if message.document is not None:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        Guest.update(made_speech=True).where(
            Guest.user_id == message.from_user.id).execute()
        logging.info(f'{name} requested file prompt')
        await file_handle(file, name, file_path, message)

    else:
        await message.answer('Можно отправлять только файлы!')


async def text_util(message, message_text):
    button = types.InlineKeyboardButton(
        text='В меню', callback_data='menu')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(button)
    ans = await add_prompt(message_text)
    await message.answer(ans, reply_markup=keyboard.adjust(1).as_markup())
