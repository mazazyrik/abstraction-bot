import os
import aiofiles
import PyPDF2

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import bot
from chat import add_prompt


import aiofiles


async def final_file_write(text, name: str):
    file_name = f"{name}_final.md"
    final_text = await add_prompt(text)

    if isinstance(final_text, str):
        final_text = final_text.encode('utf-8').decode('utf-8')

    async with aiofiles.open(file_name, 'w', encoding='utf-8') as f:
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
        msg = await message.reply(
            'Загрузка...\n\nВ данный момент среднее время обработки файла '
            '5 минут\n\nЕсли за 10 минут вам так и не '
            'пришел ответ напишите @abstractionsupport'
        )
        f = open(f'{name}.txt', 'r')
        text = f.read()

        final_file = await final_file_write(text, name)
        await bot.delete_message(message.chat.id, msg.message_id)

        file = types.FSInputFile(final_file)

        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        button2 = types.InlineKeyboardButton(
            text='Еще один файл', callback_data='text_file'
        )
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        keyboard.add(button2)

        await bot.send_document(
            message.chat.id, file, reply_markup=keyboard.adjust(
                1).as_markup()
        )
        os.remove(f"{name}.txt")
        os.remove(f"{name}_final.md")
    except FileExistsError:
        await message.reply(
            "Вы не можете отправить новый запрос, "
            "пока не закончите предыдущий!"
        )


async def handle_pdf_or_txt_server(file, message, name):
    if file.endswith('.txt'):
        f = open(f'uploaded_files/{file}', 'r')
        text = f.read()

        final_file = await final_file_write(text, name)
        await bot.delete_message(message.chat.id, message.message_id)

        file = types.FSInputFile(final_file)

        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        button2 = types.InlineKeyboardButton(
            text='Еще один файл', callback_data='text_file'
        )
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        keyboard.add(button2)

        await bot.send_document(
            message.chat.id, file, reply_markup=keyboard.adjust(
                1).as_markup()
        )
        os.remove(f"{name}_final.md")
        os.remove(f'uploaded_files/{name}')

    elif file.endswith('.pdf'):
        msg = await message.reply("")

        reader = PyPDF2.PdfReader(f'uploaded_files/{file}')
        text = ''
        for page in reader.pages:
            text += page.extract_text().encode('utf-8')

        final_file = await final_file_write(text, name)
        await bot.delete_message(message.chat.id, msg.message_id)

        file = types.FSInputFile(final_file)

        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        button2 = types.InlineKeyboardButton(
            text='Еще один файл', callback_data='text_file'
        )
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        keyboard.add(button2)

        await bot.send_document(
            message.chat.id, file, reply_markup=keyboard.adjust(
                1).as_markup()
        )
        os.remove(f"{name}_final.md")
        os.remove(f'uploaded_files/{name}')


async def handle_pdf(
        file: types.File,
        name: str,
        file_path: str,
        message: types.Message
):
    try:
        await bot.download_file(file_path, f"{name}.pdf")
        msg = await message.reply(
            'Загрузка...\n\nВ данный момент среднее время обработки файла '
            '5 минут\n\nЕсли за 10 минут вам так и не '
            'пришел ответ напишите @abstractionsupport'
        )

        reader = PyPDF2.PdfReader(f'{name}.pdf')
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        final_file = await final_file_write(text, name)
        await bot.delete_message(message.chat.id, msg.message_id)

        file = types.FSInputFile(final_file)

        button = types.InlineKeyboardButton(
            text='В меню', callback_data='menu')
        button2 = types.InlineKeyboardButton(
            text='Еще один файл', callback_data='text_file'
        )
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)
        keyboard.add(button2)

        await bot.send_document(
            message.chat.id, file, reply_markup=keyboard.adjust(
                1).as_markup()
        )
        os.remove(f"{name}.pdf")
        os.remove(f"{name}_final.md")
    except FileExistsError:
        await message.reply(
            "Вы не можете отправить новый запрос, "
            "пока не закончите предыдущий!"
        )
