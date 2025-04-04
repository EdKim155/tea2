#!/usr/bin/env python
import logging
import sys
import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)

from config import BOT_TOKEN
from states import (
    MAIN_MENU, VIEWING_CATEGORIES, VIEWING_PRODUCTS, VIEWING_PRODUCT_DETAILS,
    VIEWING_CART, CHECKOUT, AWAITING_ADDRESS, REGISTRATION, CONTACT_US
)
from handlers.commands import (
    start_command, help_command, about_command, catalog_command,
    cart_command, orders_command, profile_command, contact_command
)
from handlers.callbacks import handle_callback
from handlers.messages import (
    handle_text_message, handle_address_input, handle_contact_message
)
from handlers.registration import handle_contact

# Замена импорта MongoDB на эмуляцию базы данных
# При запуске подменяем модуль database на database_mock
import importlib.util
if os.path.exists('database_mock.py'):
    print("Используем эмуляцию базы данных вместо MongoDB")
    spec = importlib.util.spec_from_file_location("database", "database_mock.py")
    database = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database)
    sys.modules['database'] = database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Запуск бота"""
    # Проверка наличия токена
    if not BOT_TOKEN:
        logger.error("Не указан токен бота в файле .env")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Главный обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            MAIN_MENU: [
                CommandHandler("help", help_command),
                CommandHandler("about", about_command),
                CommandHandler("catalog", catalog_command),
                CommandHandler("cart", cart_command),
                CommandHandler("orders", orders_command),
                CommandHandler("profile", profile_command),
                CommandHandler("contact", contact_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message),
            ],
            VIEWING_CATEGORIES: [
                CallbackQueryHandler(handle_callback),
                CommandHandler("start", start_command),
            ],
            VIEWING_PRODUCTS: [
                CallbackQueryHandler(handle_callback),
                CommandHandler("start", start_command),
            ],
            VIEWING_PRODUCT_DETAILS: [
                CallbackQueryHandler(handle_callback),
                CommandHandler("start", start_command),
            ],
            VIEWING_CART: [
                CallbackQueryHandler(handle_callback),
                CommandHandler("start", start_command),
            ],
            CHECKOUT: [
                CallbackQueryHandler(handle_callback),
                CommandHandler("start", start_command),
            ],
            AWAITING_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address_input),
                CommandHandler("start", start_command),
            ],
            REGISTRATION: [
                MessageHandler(filters.CONTACT, handle_contact),
                CommandHandler("start", start_command),
            ],
            CONTACT_US: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message),
                CommandHandler("start", start_command),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )
    
    # Регистрируем обработчик разговора
    application.add_handler(conv_handler)
    
    logger.info("Бот запущен")
    print("Бот запущен. Чтобы остановить, нажмите Ctrl+C")
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main() 