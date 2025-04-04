from telegram import Update
from telegram.ext import ContextTypes

from config import WELCOME_MESSAGE, ABOUT_MESSAGE
from keyboards import get_main_menu_keyboard, get_categories_keyboard, get_phone_share_keyboard
from database import register_user, is_user_registered
from states import MAIN_MENU, VIEWING_CATEGORIES, REGISTRATION, get_user_context

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    
    # Регистрируем или обновляем информацию о пользователе
    register_user(user_id, first_name, last_name)
    
    # Проверяем, полностью ли зарегистрирован пользователь
    if not is_user_registered(user_id):
        await update.message.reply_html(
            WELCOME_MESSAGE + "\n\n" + 
            "Для полноценного использования магазина, пожалуйста, завершите регистрацию.",
            reply_markup=get_phone_share_keyboard()
        )
        return REGISTRATION
    
    # Если пользователь уже зарегистрирован, показываем главное меню
    await update.message.reply_html(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
<b>Команды бота:</b>

/start - Запустить бота и вернуться в главное меню
/help - Показать это сообщение
/about - Информация о магазине
/catalog - Показать каталог товаров
/cart - Просмотреть корзину
/orders - История заказов
/profile - Информация о профиле
/contact - Связаться с нами
"""
    await update.message.reply_html(help_text, reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    await update.message.reply_html(ABOUT_MESSAGE, reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /catalog"""
    await update.message.reply_html(
        "<b>🍵 Каталог чая</b>\n\nВыберите категорию:",
        reply_markup=get_categories_keyboard()
    )
    return VIEWING_CATEGORIES

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /cart"""
    from handlers.callbacks import show_cart
    return await show_cart(update, context)

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /orders"""
    from handlers.callbacks import show_orders
    return await show_orders(update, context)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /profile"""
    from handlers.callbacks import show_profile
    return await show_profile(update, context)

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /contact"""
    contact_text = """
<b>☎️ Связаться с нами</b>

Если у вас возникли вопросы или предложения, вы можете связаться с нами:

📱 Телефон: +7-XXX-XXX-XXXX
📧 Email: support@teashop.ru
⏰ Время работы: 9:00 - 21:00, без выходных

Также вы можете написать ваш вопрос в этот чат, и мы ответим в ближайшее время!
"""
    await update.message.reply_html(contact_text, reply_markup=get_main_menu_keyboard())
    return MAIN_MENU 