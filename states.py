from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Add_application(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_comment = State()


