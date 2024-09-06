from aiogram import types, F, Router

from db import UserAuth
from util_tools.utils import (
    del_premium_request,
    check_premium
)
router = Router()


@router.callback_query(F.data == 'checkpremium')
async def checkpremium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    check = check_premium(user_id)
    if check is None:
        await callback.message.answer('У вас нет премиума!\N{broken heart}')

    else:
        await callback.message.answer(
            f'У вас есть премиум! Осталось: {check} дней.'
        )


@router.callback_query(F.data == 'getpremiums')
async def get_premiums(callback: types.CallbackQuery):
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    if list(premium_users) == []:
        await callback.message.answer('Никто не имеет премиума!')
    else:
        await del_premium_request(premium_users[0].username,
                                  premium_users[0].user_id, page=1)


@router.callback_query(lambda c: 'page' in c.data)
async def next_page(callback: types.CallbackQuery):
    page = int(callback.data.split('_')[-1])
    premium_users = UserAuth.select().where(UserAuth.premium == True)
    user = None
    try:
        user = premium_users[page]
    except IndexError:
        await callback.message.answer('Больше нет пользователей!')
    if user is not None:
        await del_premium_request(user.username,
                                  user.user_id, page + 1)
