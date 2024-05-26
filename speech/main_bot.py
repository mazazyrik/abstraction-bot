# flake8: noqa
import logging
import asyncio
from main_speech import main as speech_main
import os
from ogg_to_mp3 import to_mp3
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters.command import Command
from pathlib import Path
from db import Guest, UserAuth
from threads import ThreadWithReturnValue

MY_CHAT_ID = 387435447


bot = Bot(token="7149556054:AAFPIKcoj97DvflYdaCVlFtbNRJb4QKb87I")
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


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


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if user_id == MY_CHAT_ID:
        kb = [
            [types.KeyboardButton(text='/admin')],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

        await message.answer(
            'Здарова, никитос! пришли'
            ' мне голосовое сообщение или войди в админку',
            reply_markup=keyboard
        )
    elif UserAuth.select().where(UserAuth.user_id == user_id).exists():
        await message.answer(
            'Уже есть премиум аккаунт! Вы крутой, скидывайте свое гс'
        )
    else:
        kb = [
            [types.KeyboardButton(text='/getpremium')],
            [types.KeyboardButton(text="/try")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(
            f'Привет, {username}! Что бы получить премиум, нажми /getpremium. '
            f'1 неделя = 200 рублей, 1 месяц = 600 рублей.'
            f'Переводи через СБП на Тинькофф по номеру 89771416389'
            f' с коментарием "Премиум"'
            f'Таже по комманде /try ты можешь сделать пробную расшифровку, ',
            reply_markup=keyboard
        )


@dp.message(Command("try"))
async def cmd_try(message: types.Message):
    user_id = message.from_user.id
    if Guest.select().where(Guest.user_id == user_id, Guest.made_speech == True).exists():
        kb = [
            [types.KeyboardButton(text='/getpremium')]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer('Ты уже пробовал! '
                             'Больше коспектов доступно с премиум подпиской.'
                             'Приобрести премиум можно по команде /getpremium',
                             reply_markup=keyboard)
    elif Guest.select().where(Guest.user_id == user_id, Guest.made_speech == False).exists():
        await message.answer('Отправляй свое голосовое')
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=message.from_user.username)
        await message.answer('Отправляй свое голосовое')


async def main_speech_func(message, name, msg):
    ans = await speech_main(f"{name}.mp3")

    await message.answer(ans)
    await bot.delete_message(message.chat.id, msg.message_id)


@dp.message(F.content_type.in_({'audio', 'voice'}))
async def voice_message_handler(message: types.Message):
    name = message.from_user.username
    premium_users = [user.username for user in UserAuth.select().where(
        UserAuth.premium == True)]
    aval_guests = [guest.username for guest in Guest.select().where(
        Guest.made_speech == False)]
    if name in (premium_users or aval_guests):
        if message.audio is not None:
            file_id = message.audio.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            try:
                await bot.download_file(file_path, f"{name}.mp3")
                msg = await message.reply("Загрузка...")
                await main_speech_func(message, name, msg)
                os.remove(f"{name}.mp3")
            except FileExistsError:
                await message.reply(
                    "Вы не можете отправить новый запрос, пока не закончите предыдущий!"
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
                    "Вы не можете отправить новый запрос, пока не закончите предыдущий!"
                )

    else:
        kb = [
            [types.KeyboardButton(text='/getpremium')],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(
            'У вас нет премиума! Что бы получить премиум, нажми /getpremium',
            reply_markup=keyboard
        )


async def premium_requests(username, user_id):
    kb = [
        [types.KeyboardButton(text=f"Выдать премиум {user_id}, {username}")],
        [types.KeyboardButton(text="/start")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await bot.send_message(
        MY_CHAT_ID, f'Пользователь {username} запросил премиум!',
        reply_markup=keyboard
    )


@dp.message(Command('getpremium'))
async def get_premium(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    await message.answer('Ваши данные переданы админу!')

    await premium_requests(username, user_id)


@dp.message(Command("admin"))
async def admin(message: types.Message):
    user_id = message.from_user.id
    if user_id == MY_CHAT_ID:
        kb = [
            [types.KeyboardButton(text="/getpremiums")],
            [types.KeyboardButton(text="/getpremium")],

        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(
            'Привет, админ! Вот тебе твои возможности', reply_markup=keyboard
        )
    else:
        await message.answer("Ты не админ")


@dp.message(F.text.startswith("Выдать премиум"))
async def give_premium(message: types.Message):
    args = message.text[14:]
    user_id = args.split(",")[0]
    username = (args.split(",")[1])[1:]
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username)

    if user is not None:
        await message.answer('Такой пользователь уже есть!')
    else:
        UserAuth.create(
            username=username,
            premium=True,
            user_id=int(user_id)
        )
        await message.answer('Премиум выдан!')
        await bot.send_message(int(user_id), 'Вы получили премиум!')


async def del_premium_request(username, user_id):
    kb = [
        [types.KeyboardButton(text=f"Забрать премиум {user_id}, {username}")],
        [types.KeyboardButton(text="/admin")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await bot.send_message(
        MY_CHAT_ID, f'Забрать премиум у пользователя {username}?',
        reply_markup=keyboard
    )


@dp.message(F.text.startswith("Забрать премиум"))
async def del_premium(message: types.Message):

    args = message.text[16:]
    user_id = args.split(",")[0]
    username = (args.split(",")[1])[1:]
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username)

    if user is None:
        await message.answer('Такого пользователя нет!')
    else:
        UserAuth.delete().where(
            UserAuth.user_id == int(user_id),
            UserAuth.username == username
        ).execute()
        await message.answer('Премиум удален!')
        await bot.send_message(int(user_id), 'У вас больше нет премиума!')


@dp.message(Command('getpremiums'))
async def get_premiums(message: types.Message):
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    if list(premium_users) == []:
        await message.answer('Никто не имеет премиума!')
    for user in premium_users:
        await message.answer(f'{user.username} - {user.user_id}')
        await del_premium_request(user.username, int(user.user_id))
        await asyncio.sleep(5)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
