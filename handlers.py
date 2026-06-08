import re
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext


# Кастомные импорты
from states import Add_application
from database import add_applications, get_all_applications, delete_application_by_id
from config import ADD_APPLICATION, CLIENT_APPLICATIONS, WATCH_APPLICATION, ADMIN_ID, CANCEL

router = Router()

@router.message(Command("start"), StateFilter(None))
async def start_handler(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text=ADD_APPLICATION)
    builder.button(text=CLIENT_APPLICATIONS)
    builder.button(text=WATCH_APPLICATION)

    await message.answer("Здравствуйте! Я готов принять вашу заявку ✍",
                         reply_markup=builder.as_markup(resize_keyboard=True))

# 🌟 ОТМЕНА НАХОДИТСЯ НА СВОЕМ ИДЕАЛЬНОМ МЕСТЕ — В САМОМ ВЕРХУ
@router.message(F.text == CANCEL, StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()

    builder = ReplyKeyboardBuilder()
    builder.button(text=ADD_APPLICATION)
    builder.button(text=CLIENT_APPLICATIONS)
    builder.button(text=WATCH_APPLICATION)

    builder.adjust(2, 1)

    await message.answer("❌ Заполнение заявки отменено. Данные удалены.",
                         reply_markup=builder.as_markup(resize_keyboard=True))

# 📦 ПРОСМОТР СВОИХ ЗАКАЗОВ (ДЛЯ КЛИЕНТА)
@router.message(F.text == CLIENT_APPLICATIONS)
async def show_user_applications(message: Message):
    user_id = message.from_user.id
    apps = get_all_applications()

    # Фильтруем список: оставляем только те заявки, где user_id (индекс 1) равен id текущего юзера
    user_apps = [app for app in apps if app[1] == user_id]

    if not user_apps:
        await message.answer("У вас пока нет активных заказов. 🤷‍♂️")
        return

    for app in user_apps:
        app_id = app[0]
        name = app[2]     # Исправили индекс на 2
        phone = app[3]    # Добавили вывод телефона, чтобы клиент видел всю инфу
        comment = app[4]  # Исправили индекс на 4

        inkb = InlineKeyboardBuilder()
        inkb.button(text="❌ Отменить этот заказ", callback_data=f"delete_{app_id}")

        text = f"📦 **Заказ №{app_id}**\n👤 Имя: {name}\n📞 Телефон: +{phone}\n💬 Комментарий: {comment}"

        await message.answer(text, reply_markup=inkb.as_markup())

# 🗑️ ИНЛАЙН-КНОПКА УДАЛЕНИЯ ЗАКАЗА
@router.callback_query(F.data.startswith("delete_"))
async def cancel_specific_application(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[1])

    delete_application_by_id(app_id)

    await callback.answer("Заказ отменен! 🗑️")
    await callback.message.edit_text(f"❌ **Заказ №{app_id} был успешно отменен пользователем.**")

# ✍ НАЧАЛО ЗАПОЛНЕНИЯ ЗАЯВКИ
@router.message(F.text == ADD_APPLICATION)
async def start_add_application(message: Message, state: FSMContext):
    cancel_builder = ReplyKeyboardBuilder()
    cancel_builder.button(text=CANCEL)

    await message.answer("Как вас зовут?", reply_markup=cancel_builder.as_markup(resize_keyboard=True))
    await state.set_state(Add_application.waiting_for_name)

@router.message(Add_application.waiting_for_name)
async def process_name(message: Message, state: FSMContext):

    name = message.text
    if any(char.isdigit() for char in name):
        await message.answer("Имя не должно содержать цифры! Пожалуйста, введите имя заново")
        return

    name = message.text
    await state.update_data(name=name)

    cancel_builder = ReplyKeyboardBuilder()
    cancel_builder.button(text=CANCEL)

    await message.answer("Хорошо, а теперь введите ваш номер телефона", reply_markup=cancel_builder.as_markup(resize_keyboard=True))
    await state.set_state(Add_application.waiting_for_phone)

@router.message(Add_application.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    cancel_builder = ReplyKeyboardBuilder()
    cancel_builder.button(text=CANCEL)

    phone = message.text
    cleaned_phone = re.sub(r'\D', '', phone)

    if not (re.match(r'^[78]\d{10}$', cleaned_phone)):
        await message.answer("Неверный формат номера!\nПример: +77071234567 или 87071234567", 
                             reply_markup=cancel_builder.as_markup(resize_keyboard=True))
        return

    await state.update_data(phone=cleaned_phone)
    await message.answer("Прекрасно, а теперь напишите комментарий к заявке",
                         reply_markup=cancel_builder.as_markup(resize_keyboard=True))
    await state.set_state(Add_application.waiting_for_comment)

@router.message(Add_application.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text
    await state.update_data(comment=comment)

    user_data = await state.get_data()
    name = user_data.get("name")
    phone = user_data.get("phone")
    comment_text = user_data.get("comment")

    add_applications(user_id=message.from_user.id, name=name, phone=phone, comment=comment_text)

    
    try:
        admin_alert = (
            f"🔔 **НОВАЯ ЗАЯВКА!** 🔔\n\n"
        f"👤 **Имя:** {name}\n"
        f"📞 **Телефон:** +{phone}\n"
        f"💬 **Комментарий:** {comment_text}\n"
        f"🆔 **ID Пользователя:** {message.from_user.id}")

        await message.bot.send_message(chat_id=ADMIN_ID, text=admin_alert)

    except Exception as e:
        print(f"Не удалось отправить уведомление админу: {e}")

    # После успешной отправки возвращаем меню с возможностью посмотреть свои заказы
    success_builder = ReplyKeyboardBuilder()
    success_builder.button(text=ADD_APPLICATION)
    success_builder.button(text=CLIENT_APPLICATIONS)

    await message.answer(f"✅ Спасибо! Ваша заявка успешно принята.\n\n"
        f"📋 Данные заявки:\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: +{phone}\n"
        f"💬 Комментарий: {comment_text}", 
        reply_markup=success_builder.as_markup(resize_keyboard=True))
    await state.clear()

# 👑 ПРОСМОТР ВСЕХ ЗАКАЗОВ (ТОЛЬКО ДЛЯ АДМИНА)
@router.message(F.text == WATCH_APPLICATION)
async def watch_application_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Эта функция доступна только для Админа")
        return

    apps = get_all_applications()

    if not apps:
        await message.answer("В базе данных пока нет ни одной заявки!")
        return

    response_text = "📋 **Список всех активных заявок (Панель Админа):**\n\n"

    for index, app in enumerate(apps, start=1):
        app_id = app[0]
        user_id = app[1]
        name = app[2]     # Исправили индекс на 2
        phone = app[3]    # Исправили индекс на 3
        comment = app[4]  # Исправили индекс на 4

        response_text += (
            f"#{index} Заявка (ID в базе: {app_id})\n"
            f"👤 **Имя:** {name}\n"
            f"📞 **Телефон:** +{phone}\n"
            f"💬 **Комментарий:** {comment}\n"
            f"🆔 **ID Пользователя:** {user_id}\n"
            f"-------------------------\n")
            
    await message.answer(response_text)

