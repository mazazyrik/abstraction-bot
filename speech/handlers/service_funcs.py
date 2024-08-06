# flake8: noqa
import os

from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from constants import MY_CHAT_ID, bot
from db import UserAuth, Guest
from ogg_to_mp3 import to_mp3
from util_tools.utils import check_premium, main_speech_func, user_expiry_date


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
            text='Написать конспект текста', callback_data='text'),
        types.InlineKeyboardButton(
            text='Написать конспект текста по файлу', callback_data='text_file'),
        types.InlineKeyboardButton(
            text="В админку", callback_data='admin'),
        types.InlineKeyboardButton(
            text='Обратная связь', callback_data='feedback')
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
            text='Админка', callback_data='admin'),
            types.InlineKeyboardButton(
            text="В меню", callback_data='menu')
        )

        await message.answer(
            'Здарова, никитос! пришли'
            ' мне голосовое сообщение или войди в админку',
            reply_markup=keyboard.adjust(1).as_markup()
        )
    elif UserAuth.select().where(UserAuth.user_id == user_id).exists():
        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(
            text="В меню", callback_data='menu'
        ))
        await message.answer(
            f'Привет, {username}!\N{raised hand} Я смотрю '
            f'ты уже смершарик, \N{smiling face with sunglasses}'
            f' так что вот тебе меню!\n'
            f'\nДля конспекта из аудио отправь голосовое '
            f'сообщение или файл с расширением .mp3\n',
            reply_markup=keyboard.adjust(1).as_markup()
        )

    else:
        kb = [
            types.InlineKeyboardButton(
                text='Получить премиум', callback_data='getpremium'),

            types.InlineKeyboardButton(
                text="В меню", callback_data='menu'
            ),


        ]
        keyboard = InlineKeyboardBuilder()
        keyboard.add(*kb)
        await message.answer(
            f'Привет, {username}! \N{raised hand} \n'
            f'Добро пожаловать в бота Abstraction\N{TRADE MARK SIGN}.\n'
            f'\nПрошу тебя ознакомиться '
            f'с возможностями бота и перейти в меню. \N{TRIANGULAR FLAG ON POST}\n'
            f'\nБот умеет:\n'
            f'\N{DIGIT ONE}. '
            f' Делать коспекты из голосовых сообщений или мп3 файлов до 20 мб\n'
            f'\N{DIGIT TWO}. '
            f' Писать конспекты из сообщений до 4096 символов\n'
            f'\N{DIGIT THREE}. '
            f' Писать конспекты из txt файлов\n'
            f'\N{DIGIT FOUR}. '
            f' Без преимума 1 коспект бесплатно\n'
            f'\N{DIGIT FIVE}. '
            f' С премиумом безлимитное количетво коспектов в месяц\n'
            f'\nДля конспекта из аудио отправь голосовое '
            f'сообщение или файл с расширением .mp3\n'
            f'\nТакже, если ты нашел баг или хочешь предложить новую фишку - напиши @mazwork1'
            f'\N{smiling face with sunglasses}',
            reply_markup=keyboard.adjust(1).as_markup()
        )

@router.callback_query(F.data == 'try')
async def cmd_try(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if UserAuth.select().where(
            UserAuth.premium == True, UserAuth.user_id == user_id).exists():
        await callback.message.answer('Уже есть премиум аккаунт!')
    elif Guest.select().where(
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
            'У вас нет премиума! Что бы получить премиум, нажми "Получить премиум"!',
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
    duration = int(args.split(', ')[2])
    user = UserAuth.get_or_none(
        UserAuth.user_id == int(user_id),
        UserAuth.username == username,
        UserAuth.premium == True
    )

    if user is not None:
        await callback.message.answer('Такой пользователь уже есть!',
                                      show_alert=True)
    else:
        UserAuth.create(
            username=username,
            premium=True,
            user_id=int(user_id),
            expiry_date=user_expiry_date(duration)
        )

        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu')
        ]
        keyboard = InlineKeyboardBuilder()

        keyboard.add(*kb)
        await callback.message.answer(f'Премиум выдан!\N{green heart}',
                                      reply_markup=(
                                          keyboard.adjust(1).as_markup()
                                      ))
        await bot.send_message(
            int(user_id), f'Вы получили премиум!\N{green heart}',
            reply_markup=keyboard.adjust(1).as_markup()
        )


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
        await bot.send_message(int(user_id), f'У вас больше нет премиума!\N{broken heart}',
                               reply_markup=(
            keyboard.adjust(1).as_markup()
        ))
