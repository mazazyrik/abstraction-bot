# flake8: noqa
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from db import Guest, UserAuth
from util_tools.utils import (
    premium_limit,
    File,
    check_premium,
    file_prompt,
)

router = Router()


@router.callback_query(F.data == 'text_file')
async def text_file(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(File.file)
    await callback.message.answer(
        f'Отправь мне файл для создания коспекта.\n\n'
        'Файлы принимаются только с расширениями .txt и .pdf'
    )


@router.message(File.file, F.content_type.in_({'document'}))
async def text_file_msg(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    check_premium(user_id)
    name = message.from_user.username
    if UserAuth.select().where(
        UserAuth.user_id == user_id, UserAuth.premium == True
    ):
        await file_prompt(message, user_id, name)
    elif (
        Guest.select().where(
            Guest.user_id == user_id, Guest.made_speech == True
        ).exists() or UserAuth.select().where(
            UserAuth.user_id == user_id, UserAuth.premium == False
        ).exists()
    ):
        await premium_limit(message)
    elif Guest.select().where(
        Guest.user_id == user_id, Guest.made_speech == False
    ).exists():
        await file_prompt(message, user_id, name)
    else:
        Guest.create(user_id=user_id, made_speech=False,
                     username=message.from_user.username)
        await file_prompt(message, user_id, name)
