# flake8: noqa
import os
from ogg_to_mp3 import to_mp3

from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from constants import MY_CHAT_ID, bot
from db import UserAuth, Guest
from utils import main_speech_func


router = Router()

@router.callback_query(F.data == 'menu')
async def menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(
        text='Проверить премиум', callback_data='checkpremium'),
        types.InlineKeyboardButton(
            text='Получить премиум', callback_data='getpremium'
    ),
        types.InlineKeyboardButton(
            text="Попробовать", callback_data='try'),
        types.InlineKeyboardButton(
            text="В админку", callback_data='admin'),
        types.InlineKeyboardButton(
            text='Написать конспект текста', callback_data='text')
    )
    await callback.message.edit_reply_markup(
        reply_markup=keyboard.adjust(1).as_markup()
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if user_id == MY_CHAT_ID:

        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(
            text='Админка', callback_data='admin'))

        await message.answer(
            'Здарова, никитос! пришли'
            ' мне голосовое сообщение или войди в админку',
            reply_markup=keyboard.adjust(2).as_markup()
        )
    elif UserAuth.select().where(UserAuth.user_id == user_id).exists():
        await message.answer(
            'Уже есть премиум аккаунт! Вы крутой, скидывайте свое гс'
        )
    else:
        kb = [
            types.InlineKeyboardButton(
                text='Получить премиум', callback_data='getpremium'),
            types.InlineKeyboardButton(
                text="Попробовать", callback_data='try'),
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu'
            ),
            types.InlineKeyboardButton(
                text='Написать конспект текста', callback_data='text'
            )

        ]
        keyboard = InlineKeyboardBuilder()
        keyboard.add(*kb)
        await message.answer(
            f'Привет, {username}! Чтобы получить '
            f'полный доступ - купи премиум. '
            f'Также можешь попробовать использовать голосовое сообщение, '
            f'если ты еще не пробовал!',
            reply_markup=keyboard.adjust(2).as_markup()
        )


@router.callback_query(F.data == 'try')
async def cmd_try(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if Guest.select().where(
        Guest.user_id == user_id, Guest.made_speech == True
    ).exists():

        button = types.InlineKeyboardButton(
            text='Получить премиум', callback_data='getpremium')
        keyboard = InlineKeyboardBuilder()
        keyboard.add(button)

        await callback.message.answer('Ты уже пробовал! '
                                      'Больше коспектов доступно с '
                                      'премиум подпиской.',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      )
                                      )
    elif Guest.select().where(
        Guest.user_id == user_id, Guest.made_speech == False
    ).exists():
        await callback.message.answer(
            'Отправляй свое голосовое', show_alert=True
        )
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=callback.from_user.username)
        await callback.message.answer(
            'Отправляй свое голосовое', show_alert=True
        )


@router.message(F.content_type.in_({'audio', 'voice'}))
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
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await message.answer(
            'У вас нет премиума! Что бы получить премиум, нажми /getpremium',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'admin')
async def admin(callback=types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id == MY_CHAT_ID:
        kb = [
            types.InlineKeyboardButton(
                text="Список премиум пользователей",
                callback_data='getpremiums'),

        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer(
            'Привет, админ! Вот тебе твои возможности',
            reply_markup=keyboard.adjust(2).as_markup()
        )
    else:
        await callback.answer("Ты не админ")


@router.callback_query(F.data == 'give_premium')
async def give_premium(callback: types.CallbackQuery):
    args = callback.message.text.replace('Пользователь ', '')
    args = args.replace(' запросил премиум!', '')
    username = args.split(', ')[0]
    user_id = int(args.split(', ')[1])
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username)

    if user is not None:
        await callback.message.answer('Такой пользователь уже есть!',
                                      show_alert=True)
    else:
        UserAuth.create(
            username=username,
            premium=True,
            user_id=int(user_id)
        )

        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu')
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer('Премиум выдан!',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      ))
        await bot.send_message(int(user_id), 'Вы получили премиум!')


@router.callback_query(F.data == 'del_premium')
async def del_premium(callback: types.CallbackQuery):

    args = callback.message.text.replace('Забрать премиум у пользователя ', '')
    args = args.replace('?', '')
    username = args.split(', ')[0]
    user_id = int(args.split(', ')[1])
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username)

    if user is None:
        await callback.message.answer('Такого пользователя нет!')
    else:
        UserAuth.delete().where(
            UserAuth.user_id == int(user_id),
            UserAuth.username == username
        ).execute()
        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu')
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer('Премиум удален!',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      ))
        await bot.send_message(int(user_id), 'У вас больше нет премиума!')
