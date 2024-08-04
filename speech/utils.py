from threads import ThreadWithReturnValue
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main_speech import main as speech_main
from constants import MY_CHAT_ID, bot


class Text(StatesGroup):
    text = State()


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


async def premium_requests(username, user_id):
    kb = [
        types.InlineKeyboardButton(
            text=f"Выдать премиум {username}", callback_data='give_premium'),
        types.InlineKeyboardButton(
            text="В меню", callback_data='menu')
    ]
    keyboard = InlineKeyboardBuilder()

    keyboard.add(*kb)
    await bot.send_message(
        MY_CHAT_ID, f'Пользователь {username}, запросил премиум! {user_id}',
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
