from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from states import Add_application
from database import add_applications, get_all_applications

from config import ADD_APPLICATION, WATCH_APPLICATION

import re

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):

    builder = ReplyKeyboardBuilder()

    builder.button(text=ADD_APPLICATION)
    builder.button(text=WATCH_APPLICATION)


    await message.answer("Здраствуйте я готов принять вашу заявку✍",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text==ADD_APPLICATION)
async def start_add_application(message: Message, state: FSMContext):

    

    await message.answer("Как вас зовут?")

    await state.set_state(Add_application.waiting_for_name)

@router.message(Add_application.waiting_for_name)
async def process_name(message:Message, state:FSMContext):
    name = message.text
    await state.update_data(name=name)

    await message.answer("Хорошо, а теперь введите ваш номер телефона")
    await state.set_state(Add_application.waiting_for_phone)

@router.message(Add_application.waiting_for_phone)
async def process_phone(message:Message, state:FSMContext):
    phone = message.text

    cleaned_phone = re.sub(r'\D', '', phone)

    if not (re.match(r'^[78]\d{10}$', cleaned_phone)):
        await message.answer("неверный формат номера!\nПример: +77071234567 или 87071234567")
        return

    await state.update_data(phone=cleaned_phone)
    await message.answer("Прекрасно, а теперь напшите коментарии к заявке")
    await state.set_state(Add_application.waiting_for_comment)

@router.message(Add_application.waiting_for_comment)
async def process_comment(message:Message, state:FSMContext):
    comment = message.text
    await state.update_data(comment=comment)

    user_data = await state.get_data()
    name = user_data.get("name")
    phone = user_data.get("phone")
    comment = user_data.get("comment")

    add_applications(name=name, phone=phone, comment=comment)

    await message.answer(
        f"✅ Спасибо! Ваша заявка успешно принята.\n\n"
        f"📋 Данные заявки:\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: +{phone}\n"
        f"💬 Комментарий: {comment}")

    await state.clear()

@router.message(F.text==WATCH_APPLICATION)
async def watch_application_handler(message:Message):

    apps = get_all_applications()

    if not apps:
        await message.answer("В базе данных пока нет ни одной заявки!")
        return

    response_text = "📋 **Список всех активных заявок:**\n\n"

    for index , app in enumerate(apps, start=1):
        name = app[0]
        phone = app[1]
        comment = app[2]

        response_text += (
            f"{index} заявка\n"
            f"👤 **Имя:** {name}\n"
            f"📞 **Телефон:** +{phone}\n"
            f"💬 **Комментарий:** {comment}\n"
            f"-------------------------\n")
    await message.answer(response_text)









