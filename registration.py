from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from database import update_user_phone, get_user
from keyboards import get_main_menu_keyboard
from states import MAIN_MENU, REGISTRATION, get_user_context
from config import REGISTER_MESSAGE

async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает у пользователя номер телефона"""
    await update.message.reply_html(REGISTER_MESSAGE)
    return REGISTRATION

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученный контакт для регистрации"""
    user = update.effective_user
    user_id = user.id
    
    # Получаем данные контакта
    contact = update.message.contact
    phone_number = contact.phone_number
    
    # Обновляем данные пользователя
    now = datetime.now()
    update_success = update_user_phone(user_id, phone_number, now)
    
    if update_success:
        await update.message.reply_html(
            """
<b>✅ Регистрация успешно завершена!</b>

Теперь вы можете пользоваться всеми функциями нашего магазина.

Добро пожаловать в мир изысканного чая! 🍵
""",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_html(
            """
<b>❌ Произошла ошибка при регистрации</b>

Пожалуйста, попробуйте еще раз или свяжитесь с администратором.
""",
            reply_markup=get_main_menu_keyboard()
        )
    
    return MAIN_MENU

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает профиль пользователя"""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data:
        await update.message.reply_html(
            "❌ Информация о вашем профиле не найдена. Пожалуйста, перезапустите бота командой /start",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    # Форматируем данные пользователя
    first_name = user_data.get('first_name', 'Не указано')
    last_name = user_data.get('last_name', '')
    phone = user_data.get('phone_number', 'Не указан')
    registered_at = user_data.get('registered_at')
    
    # Форматируем дату регистрации
    if registered_at:
        if hasattr(registered_at, 'strftime'):
            registered_date = registered_at.strftime('%d.%m.%Y %H:%M')
        else:
            registered_date = str(registered_at)
    else:
        registered_date = 'Регистрация не завершена'
    
    profile_text = f"""
<b>📱 Ваш профиль</b>

<b>Имя:</b> {first_name} {last_name}
<b>Телефон:</b> {phone}
<b>Дата регистрации:</b> {registered_date}
"""
    
    # Добавляем кнопку для изменения данных, если нужно
    await update.message.reply_html(profile_text, reply_markup=get_main_menu_keyboard())
    return MAIN_MENU 