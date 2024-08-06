from constants import bot
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from chat import add_prompt
import aiofiles


async def final_file_write(text, name):
    file_name = f'{name}_final.txt'
    final_text = await add_prompt(text)

    async with aiofiles.open(file_name, 'w') as f:
        await f.write(final_text)
    return file_name


async def handle_file(
        file: types.File,
        name: str,
        file_path: str,
        message: types.Message
):
    try:
        await bot.download_file(file_path, f"{name}.txt")
        msg = await message.reply("Загрузка...")
        f = open(f'{name}.txt', 'r')
        text = f.read()

        final_file = await final_file_write(text, name)
        await bot.delete_message(message.chat.id, msg.message_id)

        file = types.FSInputFile(final_file)

        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)

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
