import asyncio
from main_speech import main as speech_main
import os
from ogg_to_mp3 import to_mp3
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import F
from aiogram.filters.command import Command
from pathlib import Path


bot = Bot(token="7149556054:AAFPIKcoj97DvflYdaCVlFtbNRJb4QKb87I")
dp = Dispatcher()


async def handle_file(file: types.File, file_name: str, path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)

    await bot.download_file(
        file_path=file.file_path, destination=f"{path}/{file_name}"
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("скинь свой файл в голосовом сообщении")


@dp.message(F.voice)
async def voice_message_handler(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    name = message.from_user.first_name
    await bot.download_file(file_path, f"{name}.ogg")

    to_mp3(f"{name}.ogg")

    await message.answer(speech_main(f"{name}.mp3"))

    os.remove(f"{name}.ogg")
    os.remove(f"{name}.mp3")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
