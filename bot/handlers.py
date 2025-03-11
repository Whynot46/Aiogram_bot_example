from aiogram.filters.command import Command
from aiogram import F, Bot
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
import bot.keyboards as kb
import bot.database.db as db
import bot.services.google_api_service as google_disk
from bot.states import *
from bot.config import Config
from bot.logger import logger, error_handler


router = Router()


@error_handler
@router.message(F.text, Command("start"))
async def start_loop(message: Message, state: FSMContext):
    if not await db.is_old(message.from_user.id):
        await state.set_state(Register_steps.fullname)
        await message.answer("Введи своё ФИО:")
    else:
        if await db.is_user_active(message.from_user.id):
            user_fullname = await db.get_fullname(message.from_user.id)
            await message.answer(f"Приветствую Вас, {user_fullname}!", reply_markup=await kb.get_main_menu_keyboard())
        else:
            await message.answer(f"Администратор деактивировал ваш аккаунт", reply_markup=await kb.remove_keyboard())


@error_handler
@router.message(Register_steps.fullname)
async def registration(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    register_data = await state.get_data()
    if len((register_data["fullname"]).split(" "))==3:
        lastname, firstname, middlename = (register_data["fullname"]).split(" ")
        if await db.is_register(firstname, middlename, lastname):
            await db.update_user_id(message.from_user.id, firstname, middlename, lastname)
            await message.answer(f"Приветствую Вас, {register_data['fullname']}!", reply_markup=await kb.get_main_menu_keyboard())
            await state.clear()
        else:
            await message.answer("Данный пользователь не зарегистрирован")
    else:
        await message.answer("Некорректный формат ФИО!")
        await state.set_state(Register_steps.fullname)
        await message.answer("Введи своё ФИО:")


@error_handler
@router.message(F.text == "Заполнить отчёты")
async def chouse_shift(message: Message, state: FSMContext):
    pass


@error_handler
async def send_morning_notification(bot):
    try:
        user_ids = await db.get_all_user_id()
        for user_id in user_ids:
            await bot.send_message(user_id, "Утреннее уведомление", reply_markup=await kb.get_reply_keyboard())
    except Exception as error:
        print(f"Ошибка при отправке утреннего уведомления: {error}")


@error_handler
async def send_evening_notification(bot):
    try:
        user_ids = await db.get_all_user_id()
        for user_id in user_ids:
            await bot.send_message(user_id, "Вечернее уведомление", reply_markup=await kb.get_reply_keyboard())
    except Exception as error:
        print(f"Ошибка при отправке вечернего уведомления: {error}")