# flake8: noqa
import logging
import os

from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from constants import MY_CHAT_ID, bot
from db import UserAuth, Guest
from ogg_to_mp3 import to_mp3
from util_tools.utils import (
    check_premium,
    main_speech_func,
    user_expiry_date,
    Voice, 
    bot_get_file, 
    FileName,
)
from server import get_file
from util_tools.file_handler import handle_pdf_or_txt_server


router = Router()


@router.callback_query(F.data == 'menu')
async def menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(
            text="Попробовать",
            callback_data='try'),
        types.InlineKeyboardButton(
            text='Конспект из голосового', callback_data='voice'),
        types.InlineKeyboardButton(
            text='Конспект сообщения', callback_data='text'),
        types.InlineKeyboardButton(
            text='Конспект файла', callback_data='text_file'),
        types.InlineKeyboardButton(
            text='Получить премиум', callback_data='getpremium'),
        types.InlineKeyboardButton(
            text='Проверить премиум', callback_data='checkpremium'),
        types.InlineKeyboardButton(
            text='Обратная связь', callback_data='feedback'),
    )
    await callback.message.edit_reply_markup(
        reply_markup=keyboard.adjust(1).as_markup()
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    check_premium(user_id)
    name = message.from_user.first_name
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
            f'Привет, {name}!\N{raised hand} Я смотрю '
            f'ты уже смершарик, \N{smiling face with sunglasses}'
            f' так что вот тебе меню!\n'
            f'\nДля конспекта из аудио отправь голосовое '
            f'сообщение или файл с расширением .mp3\n',
            reply_markup=keyboard.adjust(1).as_markup()
        )

    else:
        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu'
            ),


        ]
        keyboard = InlineKeyboardBuilder()
        keyboard.add(*kb)
        await message.answer(
            f'Привет, {name}! \N{raised hand} \n'
            f'Добро пожаловать в бота Abstraction\N{TRADE MARK SIGN}.\n'
            f'\nПрошу тебя ознакомиться '
            f'с возможностями бота и перейти в меню. \N{TRIANGULAR FLAG ON POST}\n'
            f'\nПЕРВЫЙ КОНСПЕКТ БЕСПЛАТНО \N{money-mouth face}.\n'
            f'\nБот умеет:\n'
            f'\N{DIGIT ONE}. '
            f' Делать конспекты из голосовых сообщений\n'
            f'\N{DIGIT TWO}. '
            f' Писать конспекты из сообщений\n'
            f'\N{DIGIT THREE}. '
            f' Писать конспекты из файлов файлов\n'
            f'\nТакже, если ты нашел баг или хочешь предложить новую фишку - напиши @mazwork1'
            f'\N{smiling face with sunglasses}',
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'try')
async def cmd_try(callback: types.CallbackQuery, state: FSMContext):
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
        await state.set_state(Voice.voice)
        await callback.message.answer(
            'Отправляй свое голосовое', show_alert=True
        )
    else:
        await state.set_state(Voice.voice)

        Guest.create(user_id=user_id, made_speech=False,
                     username=callback.from_user.username)
        await callback.message.answer(
            'Отправляй свое голосовое', show_alert=True
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


@router.callback_query(F.data == 'voice')
async def voice(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Voice.voice)
    await callback.message.answer(
        f'Отправь голосовое сообщение или мп3 файл.\n\n'
        'Если у тебя айфон, то ты можешь '
        'поделиться записью с диктофона и отправить боту.'
    )


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


@router.callback_query(F.data == 'loaded')
async def loaded(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FileName.name)
    await callback.message.edit_text('Отлично! Вставь название файла и жди конспект!')


@router.message(FileName.name)
async def download_file(message: types.Message, state: FSMContext):
    name = message.text
    await state.clear()
    await message.reply(
        f'Загрузка...\n\n'
        'Длинные аудиозаписи могут долго'
        ' обрабатываться из-за высокой нагрузки.'
    )
    await get_file(name, message)
    if name.endswith('.mp3'):
        await main_speech_func(message, name, message)
    elif name.endswith('.txt') or name.endswith('.pdf'):
        logging.info(
            'file donloaded and calculations are ready to prepare'
        )
        await handle_pdf_or_txt_server(name, message, name)
