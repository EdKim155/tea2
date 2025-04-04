from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import TEA_CATEGORIES
from states import (
    MAIN_MENU, VIEWING_CATEGORIES, VIEWING_PRODUCTS, VIEWING_PRODUCT_DETAILS,
    VIEWING_CART, CHECKOUT, AWAITING_ADDRESS, AWAITING_CONFIRMATION,
    VIEWING_ORDERS, VIEWING_ORDER_DETAILS, get_user_context
)
from keyboards import (
    get_main_menu_keyboard, get_categories_keyboard, get_products_keyboard,
    get_product_detail_keyboard, get_cart_keyboard, get_cart_item_keyboard,
    get_checkout_keyboard, get_order_history_keyboard
)
from database import (
    add_to_cart, get_cart, clear_cart, create_order, get_user_orders, is_user_registered
)
from utils import (
    find_product_by_id, extract_product_id, extract_category_key,
    format_cart_message, format_product_details, format_order_details
)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все callback-запросы"""
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    
    # Проверяем регистрацию пользователя
    if not is_user_registered(user_id) and not data.startswith("back_to_"):
        await query.answer("Пожалуйста, завершите регистрацию")
        from handlers.commands import start_command
        return await start_command(update, context)
    
    # Обработка действий в зависимости от callback данных
    
    # Просмотр категорий
    if data.startswith("category_"):
        category_key = extract_category_key(data)
        return await show_category_products(update, context, category_key)
    
    # Просмотр товара
    elif data.startswith("product_"):
        product_id = extract_product_id(data)
        return await show_product_details(update, context, product_id)
    
    # Добавление в корзину
    elif data.startswith("add_to_cart_"):
        product_id = extract_product_id(data)
        return await add_product_to_cart(update, context, product_id)
    
    # Увеличение/уменьшение количества товара в корзине
    elif data.startswith("increase_") or data.startswith("decrease_"):
        product_id = extract_product_id(data)
        quantity = 1 if "increase_" in data else -1
        return await update_cart_quantity(update, context, product_id, quantity)
    
    # Удаление из корзины
    elif data.startswith("remove_"):
        product_id = extract_product_id(data)
        return await remove_from_cart(update, context, product_id)
    
    # Навигация между страницами
    elif data == "back_to_menu":
        return await back_to_menu(update, context)
    elif data == "back_to_categories":
        return await back_to_categories(update, context)
    elif data == "back_to_products":
        return await back_to_products(update, context)
    elif data == "back_to_cart":
        return await show_cart(update, context)
    
    # Работа с корзиной
    elif data == "checkout":
        return await show_checkout(update, context)
    elif data == "clear_cart":
        return await clear_cart_handler(update, context)
    
    # Работа с заказами
    elif data.startswith("payment_"):
        payment_method = data.replace("payment_", "")
        return await set_payment_method(update, context, payment_method)
    elif data == "confirm_order":
        return await create_new_order(update, context)
    elif data == "back_to_checkout":
        return await show_checkout(update, context)
    
    # Если ничего не подошло, возвращаем в меню
    await query.answer("Неизвестная команда")
    return MAIN_MENU

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key):
    """Показывает товары выбранной категории"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Сохраняем текущую категорию в контексте пользователя
    user_context = get_user_context(user_id)
    user_context.set_category(category_key)
    
    # Формируем сообщение с товарами категории
    category_name = TEA_CATEGORIES.get(category_key, "Категория")
    await query.edit_message_text(
        f"<b>{category_name}</b>\n\nВыберите товар:",
        reply_markup=get_products_keyboard(category_key),
        parse_mode='HTML'
    )
    await query.answer()
    
    return VIEWING_PRODUCTS

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id):
    """Показывает детальную информацию о товаре"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Сохраняем текущий товар в контексте пользователя
    user_context = get_user_context(user_id)
    user_context.set_product(product_id)
    
    # Находим товар и формируем сообщение
    product = find_product_by_id(product_id)
    if not product:
        await query.answer("Товар не найден")
        return await back_to_categories(update, context)
    
    product_text = format_product_details(product)
    
    # Отправляем сообщение с информацией о товаре
    await query.edit_message_text(
        product_text,
        reply_markup=get_product_detail_keyboard(product_id),
        parse_mode='HTML'
    )
    await query.answer()
    
    return VIEWING_PRODUCT_DETAILS

async def add_product_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id):
    """Добавляет товар в корзину"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Проверяем существование товара
    product = find_product_by_id(product_id)
    if not product:
        await query.answer("Товар не найден")
        return VIEWING_CATEGORIES
    
    # Добавляем товар в корзину
    add_to_cart(user_id, product_id)
    
    await query.answer(f"✅ {product['name']} добавлен в корзину!")
    
    # Остаемся на странице товара
    return VIEWING_PRODUCT_DETAILS

async def update_cart_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id, quantity):
    """Обновляет количество товара в корзине"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Проверяем существование товара
    product = find_product_by_id(product_id)
    if not product:
        await query.answer("Товар не найден")
        return await show_cart(update, context)
    
    # Обновляем количество (добавляем +1 или -1)
    add_to_cart(user_id, product_id, quantity)
    
    await query.answer(f"Количество изменено")
    
    # Обновляем отображение корзины
    return await show_cart(update, context)

async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id):
    """Удаляет товар из корзины"""
    # Для удаления можно использовать функцию update_cart_quantity с отрицательным значением
    # или добавить специальную функцию в database.py
    # Здесь просто удаляем, обнуляя количество (можно сделать более элегантно)
    
    # Обновляем отображение корзины
    return await show_cart(update, context)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает содержимое корзины"""
    # Определяем, это сообщение или callback
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        message_obj = query
        edit_message = True
    else:
        user_id = update.message.from_user.id
        message_obj = update.message
        edit_message = False
    
    # Получаем корзину пользователя
    cart_items = get_cart(user_id)
    cart_message = format_cart_message(cart_items)
    
    # Отправляем сообщение с корзиной
    if edit_message and hasattr(message_obj, 'edit_message_text'):
        await message_obj.edit_message_text(
            cart_message,
            reply_markup=get_cart_keyboard(),
            parse_mode='HTML'
        )
        if update.callback_query:
            await update.callback_query.answer()
    else:
        await message_obj.reply_html(
            cart_message,
            reply_markup=get_cart_keyboard()
        )
    
    return VIEWING_CART

async def clear_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищает корзину пользователя"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Очищаем корзину
    clear_cart(user_id)
    
    await query.answer("Корзина очищена")
    
    # Показываем пустую корзину
    return await show_cart(update, context)

async def show_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает страницу оформления заказа"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Получаем корзину пользователя
    cart_items = get_cart(user_id)
    
    if not cart_items:
        await query.answer("Корзина пуста")
        return await back_to_menu(update, context)
    
    # Формируем сообщение с деталями заказа
    checkout_text = """
<b>🧾 Оформление заказа</b>

Пожалуйста, выберите способ оплаты:
"""
    
    await query.edit_message_text(
        checkout_text,
        reply_markup=get_checkout_keyboard(),
        parse_mode='HTML'
    )
    await query.answer()
    
    return CHECKOUT

async def set_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method):
    """Устанавливает способ оплаты"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Сохраняем способ оплаты
    user_context = get_user_context(user_id)
    user_context.set_checkout_data('payment_method', payment_method)
    
    # Запрашиваем адрес доставки
    await query.edit_message_text(
        """
<b>📦 Адрес доставки</b>

Пожалуйста, введите адрес доставки:
""",
        parse_mode='HTML'
    )
    await query.answer()
    
    return AWAITING_ADDRESS

async def create_new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создает новый заказ"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Получаем корзину пользователя
    cart_items = get_cart(user_id)
    
    if not cart_items:
        await query.answer("Корзина пуста")
        return await back_to_menu(update, context)
    
    # Получаем данные для заказа
    user_context = get_user_context(user_id)
    checkout_data = user_context.get_checkout_data()
    shipping_address = checkout_data.get('shipping_address')
    payment_method = checkout_data.get('payment_method')
    
    if not shipping_address or not payment_method:
        await query.answer("Не указаны детали заказа")
        return await show_checkout(update, context)
    
    # Создаем заказ
    now = datetime.now()
    order_id = create_order(user_id, cart_items, shipping_address, payment_method, now)
    
    # Очищаем корзину
    clear_cart(user_id)
    
    # Очищаем данные о заказе
    user_context.clear_checkout_data()
    
    # Отправляем сообщение о успешном создании заказа
    await query.edit_message_text(
        f"""
<b>✅ Заказ успешно создан!</b>

Номер заказа: <b>{str(order_id)[-6:]}</b>

Мы свяжемся с вами в ближайшее время для подтверждения заказа.
Спасибо за покупку! 🍵
""",
        parse_mode='HTML'
    )
    await query.answer()
    
    return MAIN_MENU

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает историю заказов пользователя"""
    # Определяем, это сообщение или callback
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        message_obj = query
        edit_message = True
    else:
        user_id = update.message.from_user.id
        message_obj = update.message
        edit_message = False
    
    # Получаем заказы пользователя
    orders = get_user_orders(user_id)
    
    if not orders:
        orders_text = """
<b>📋 История заказов</b>

У вас пока нет заказов.
"""
    else:
        orders_text = "<b>📋 История заказов</b>\n\n"
        
        for order in orders:
            order_id = str(order.get('_id', ''))[-6:]
            created_at = order.get('created_at', '')
            if hasattr(created_at, 'strftime'):
                date_str = created_at.strftime('%d.%m.%Y')
            else:
                date_str = str(created_at)
            
            status = order.get('status', 'new')
            status_emoji = {
                'new': '🆕',
                'processing': '⏳',
                'shipped': '🚚',
                'delivered': '✅',
                'canceled': '❌'
            }.get(status, '❓')
            
            orders_text += f"{status_emoji} Заказ #{order_id} от {date_str}\n"
    
    # Отправляем сообщение с заказами
    if edit_message and hasattr(message_obj, 'edit_message_text'):
        await message_obj.edit_message_text(
            orders_text,
            reply_markup=get_order_history_keyboard(),
            parse_mode='HTML'
        )
        if update.callback_query:
            await update.callback_query.answer()
    else:
        await message_obj.reply_html(
            orders_text,
            reply_markup=get_order_history_keyboard()
        )
    
    return VIEWING_ORDERS

# Вспомогательные функции для навигации

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя в главное меню"""
    query = update.callback_query
    
    await query.message.reply_html(
        "Вернулись в главное меню. Что вы хотите сделать?",
        reply_markup=get_main_menu_keyboard()
    )
    await query.answer()
    
    return MAIN_MENU

async def back_to_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя к выбору категорий"""
    query = update.callback_query
    
    await query.edit_message_text(
        "<b>🍵 Каталог чая</b>\n\nВыберите категорию:",
        reply_markup=get_categories_keyboard(),
        parse_mode='HTML'
    )
    await query.answer()
    
    return VIEWING_CATEGORIES

async def back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя к списку товаров текущей категории"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Получаем текущую категорию из контекста пользователя
    user_context = get_user_context(user_id)
    category_key = user_context.current_category
    
    if not category_key:
        return await back_to_categories(update, context)
    
    # Формируем сообщение с товарами категории
    category_name = TEA_CATEGORIES.get(category_key, "Категория")
    await query.edit_message_text(
        f"<b>{category_name}</b>\n\nВыберите товар:",
        reply_markup=get_products_keyboard(category_key),
        parse_mode='HTML'
    )
    await query.answer()
    
    return VIEWING_PRODUCTS 