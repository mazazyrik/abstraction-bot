import logging

from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from constants import MY_CHAT_ID
from db import UserAuth, Guest
from util_tools.utils import (
    check_premium,
    main_speech_func,
    Voice,
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
            'ты уже смешарик, \N{smiling face with sunglasses}'
            ' так что вот тебе меню!\n',
            reply_markup=keyboard.adjust(1).as_markup()
        )

    elif Guest.select().where(Guest.user_id == user_id).exists():
        name = message.from_user.full_name
        kb = [
            types.InlineKeyboardButton(
                text="В меню", callback_data='menu'
            ),


        ]
        keyboard = InlineKeyboardBuilder()
        keyboard.add(*kb)
        await message.answer(
            f'Привет, {name}! \N{raised hand} \n'
            'Добро пожаловать в бота Abstraction\N{TRADE MARK SIGN}.\n'
            '\nПрошу тебя ознакомиться '
            'с возможностями бота и перейти в меню. '
            '\N{TRIANGULAR FLAG ON POST}\n'
            '\nПЕРВЫЙ КОНСПЕКТ БЕСПЛАТНО \N{money-mouth face}.\n'
            '\nБот умеет:\n'
            '\N{DIGIT ONE}. '
            ' Делать конспекты из голосовых сообщений\n'
            '\N{DIGIT TWO}. '
            ' Писать конспекты из сообщений\n'
            '\N{DIGIT THREE}. '
            ' Писать конспекты из файлов файлов\n'
            '\nТакже, если ты нашел баг или хочешь предложить новую фишку - '
            'напиши @abstractionsupport'
            '\N{smiling face with sunglasses}',
            reply_markup=keyboard.adjust(1).as_markup()
        )
    else:
        kb = [
            types.InlineKeyboardButton(
                text="Я согласен", callback_data='terms'
            ),


        ]
        keyboard = InlineKeyboardBuilder()
        keyboard.add(*kb)
        conditions_of_use = (
            "1. Разрешение на запись\n"
            "Пользователи обязаны получать разрешение на запись лекций"
            " у преподавателей "
            "или других правообладателей. Ответственность за соблюдение"
            " данного требования "
            "лежит исключительно на пользователях.\n\n"

            "2. Хранение аудиоданных\n"
            "Аудиоданные, загружаемые пользователями, временно "
            "хранятся на сервере для "
            "обработки запросов. Мы не гарантируем сохранность данных"
            " после завершения обработки.\n\n"

            "3. Авторские права на файлы\n"
            "Все файлы, загружаемые пользователями, должны быть согласованы"
            " с правообладателями. "
            "Мы не несем ответственности за нарушение авторских прав.\n\n"

            "4. Сбор личных данных\n"
            "Бот может собирать некоторые личные данные, такие как никнейм"
            " и ID пользователя. "
            "Эти данные используются исключительно для функционирования бота"
            " и не передаются третьим лицам.\n\n"

            "5. Генерируемые данные\n"
            "Все данные, сгенерированные ботом, не являются учебными"
            " и могут использоваться "
            "пользователями только в личных целях."
            " Мы не несем ответственности за последствия "
            "их использования.\n\n"

            "6. Отказ от ответственности\n"
            "Используя данного бота, вы подтверждаете, что ознакомлены"
            " с вышеуказанными условиями "
            "и принимаете на себя полную ответственность за свои действия.\n\n"

            "Пожалуйста, используйте бот ответственно!"
        )

        await message.answer(
            'Перед использованием прошу ознакомиться '
            'с условиями использования бота.\n'
            'Все права защищены. \n'
            'Если вы согласны с условиями, нажмите "Я согласен"\n'
            + conditions_of_use,
            reply_markup=keyboard.adjust(1).as_markup()
        )


@router.callback_query(F.data == 'terms')
async def terms(callback: types.CallbackQuery):
    name = callback.from_user.full_name
    kb = [
        types.InlineKeyboardButton(
            text="В меню", callback_data='menu'
        ),


    ]
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*kb)
    await callback.message.answer(
        f'Привет, {name}! \N{raised hand} \n'
        'Добро пожаловать в бота Abstraction\N{TRADE MARK SIGN}.\n'
        '\nПрошу тебя ознакомиться '
        'с возможностями бота и перейти в меню. '
        '\N{TRIANGULAR FLAG ON POST}\n'
        '\nПЕРВЫЙ КОНСПЕКТ БЕСПЛАТНО \N{money-mouth face}.\n'
        '\nБот умеет:\n'
        '\N{DIGIT ONE}. '
        ' Делать конспекты из голосовых сообщений\n'
        '\N{DIGIT TWO}. '
        ' Писать конспекты из сообщений\n'
        '\N{DIGIT THREE}. '
        ' Писать конспекты из файлов файлов\n'
        '\nТакже, если ты нашел баг или хочешь предложить новую фишку - '
        'напиши @abstractionsupport'
        '\N{smiling face with sunglasses}',
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


@router.callback_query(F.data == 'loaded')
async def loaded(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FileName.name)
    await callback.message.edit_text(
        'Отлично! Вставь название файла и жди конспект!'
    )


@router.message(FileName.name)
async def download_file(message: types.Message, state: FSMContext):
    name = message.text
    await state.clear()
    await message.reply(
        'Загрузка...\n\n'
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
