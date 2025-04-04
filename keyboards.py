from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from config import TEA_CATEGORIES, TEA_PRODUCTS

def get_main_menu_keyboard():
    """Основное меню"""
    buttons = [
        [KeyboardButton("🛍️ Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("📱 Мой профиль"), KeyboardButton("📋 Мои заказы")],
        [KeyboardButton("ℹ️ О магазине"), KeyboardButton("☎️ Связаться с нами")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_categories_keyboard():
    """Клавиатура с категориями чая"""
    buttons = []
    row = []
    
    # Создаем ряды по 2 кнопки
    for key, name in TEA_CATEGORIES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"category_{key}"))
        
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    # Добавляем оставшиеся кнопки
    if row:
        buttons.append(row)
    
    # Добавляем кнопку назад
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(buttons)

def get_products_keyboard(category_key):
    """Клавиатура с товарами выбранной категории"""
    buttons = []
    
    for product in TEA_PRODUCTS.get(category_key, []):
        # Одна кнопка для каждого продукта
        buttons.append([InlineKeyboardButton(
            f"{product['name']} - {product['price']} ₽", 
            callback_data=f"product_{product['id']}"
        )])
    
    # Добавляем кнопку назад к категориям
    buttons.append([InlineKeyboardButton("🔙 К категориям", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(buttons)

def get_product_detail_keyboard(product_id):
    """Клавиатура для страницы товара"""
    buttons = [
        [InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}")],
        [InlineKeyboardButton("🔙 К списку товаров", callback_data="back_to_products")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_cart_keyboard():
    """Клавиатура для корзины"""
    buttons = [
        [InlineKeyboardButton("🧾 Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 В каталог", callback_data="back_to_categories")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_cart_item_keyboard(product_id):
    """Клавиатура для товара в корзине"""
    buttons = [
        [
            InlineKeyboardButton("➖", callback_data=f"decrease_{product_id}"),
            InlineKeyboardButton("❌", callback_data=f"remove_{product_id}"),
            InlineKeyboardButton("➕", callback_data=f"increase_{product_id}")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_phone_share_keyboard():
    """Клавиатура запроса номера телефона"""
    button = KeyboardButton("📱 Поделиться номером телефона", request_contact=True)
    return ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)

def get_checkout_keyboard():
    """Клавиатура для выбора способа оплаты"""
    buttons = [
        [InlineKeyboardButton("💳 Картой онлайн", callback_data="payment_card")],
        [InlineKeyboardButton("💵 Наличными при получении", callback_data="payment_cash")],
        [InlineKeyboardButton("🔙 Назад к корзине", callback_data="back_to_cart")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_confirm_order_keyboard():
    """Клавиатура для подтверждения заказа"""
    buttons = [
        [InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton("🔙 Изменить данные", callback_data="back_to_checkout")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_order_history_keyboard():
    """Клавиатура для истории заказов"""
    buttons = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(buttons) 