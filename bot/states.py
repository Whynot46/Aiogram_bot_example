from aiogram.fsm.state import StatesGroup, State


# Регистрация
class Register_steps(StatesGroup):
    fullname = State()  # ФИО