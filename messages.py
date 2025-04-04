from telegram import Update
from telegram.ext import ContextTypes

from states import MAIN_MENU, AWAITING_ADDRESS, CONTACT_US, get_user_context
from keyboards import get_main_menu_keyboard, get_confirm_order_keyboard
from database import is_user_registered

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Проверяем регистрацию пользователя
    if not is_user_registered(user_id):
        from handlers.commands import start_command
        return await start_command(update, context)
    
    # Обработка сообщений в зависимости от текста
    if text == "🛍️ Каталог":
        from handlers.commands import catalog_command
        return await catalog_command(update, context)
    
    elif text == "🛒 Корзина":
        from handlers.callbacks import show_cart
        return await show_cart(update, context)
    
    elif text == "📱 Мой профиль":
        from handlers.registration import show_profile
        return await show_profile(update, context)
    
    elif text == "📋 Мои заказы":
        from handlers.callbacks import show_orders
        return await show_orders(update, context)
    
    elif text == "ℹ️ О магазине":
        from handlers.commands import about_command
        return await about_command(update, context)
    
    elif text == "☎️ Связаться с нами":
        from handlers.commands import contact_command
        return await contact_command(update, context)
    
    else:
        # По умолчанию пользователь находится в главном меню
        return await handle_unknown_message(update, context)

async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает неизвестные сообщения"""
    await update.message.reply_text(
        "Извините, я не понимаю эту команду. Пожалуйста, используйте меню или /help для списка команд.",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU

async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод адреса доставки"""
    user_id = update.effective_user.id
    address = update.message.text
    
    # Сохраняем адрес доставки
    user_context = get_user_context(user_id)
    user_context.set_checkout_data('shipping_address', address)
    
    # Показываем сообщение для подтверждения заказа
    checkout_data = user_context.get_checkout_data()
    payment_method = checkout_data.get('payment_method', 'Не выбран')
    
    # Форматируем способ оплаты
    if payment_method == 'card':
        payment_text = '💳 Оплата картой онлайн'
    elif payment_method == 'cash':
        payment_text = '💵 Оплата наличными при получении'
    else:
        payment_text = 'Способ оплаты не выбран'
    
    confirmation_text = f"""
<b>Подтверждение заказа</b>

<b>Адрес доставки:</b>
{address}

<b>Способ оплаты:</b>
{payment_text}

Пожалуйста, проверьте данные и подтвердите заказ.
"""
    await update.message.reply_html(
        confirmation_text,
        reply_markup=get_confirm_order_keyboard()
    )
    
    return CONTACT_US

async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения в режиме обратной связи"""
    user_id = update.effective_user.id
    message = update.message.text
    
    # Здесь можно добавить логику сохранения сообщения или отправки администратору
    
    await update.message.reply_html(
        """
<b>✅ Ваше сообщение отправлено!</b>

Спасибо за обращение. Мы рассмотрим ваш запрос и ответим в ближайшее время.
""",
        reply_markup=get_main_menu_keyboard()
    )
    
    return MAIN_MENU 