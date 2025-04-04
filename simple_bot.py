from datetime import datetime, timedelta
from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Определение констант
STATE_MAIN = "main"
STATE_AWAITING_ADDRESS = "awaiting_address"
STATE_AWAITING_COMMENT = "awaiting_comment"
STATE_AWAITING_PROMO = "awaiting_promo"
STATE_AWAITING_NAME = "awaiting_name"

# Администраторы и состояния администратора
ADMIN_IDS = [5512345678, 328924878]  # Замените на реальные ID администраторов
ADMIN_PASSWORD = "admin123"  # Замените на реальный пароль
ADMIN_STATE_MAIN = "admin_main"
ADMIN_STATE_ORDERS = "admin_orders"
ADMIN_STATE_PRODUCTS = "admin_products" 
ADMIN_STATE_LOYALTY = "admin_loyalty"
ADMIN_STATE_PROMO = "admin_promo"
ADMIN_STATE_STATS = "admin_stats"
ADMIN_STATE_AWAITING_PRODUCT_DATA = "admin_awaiting_product_data"

# Словарь для отслеживания состояний пользователей
USER_STATES = {}

# Словарь для системы лояльности
LOYALTY = {}
LOYALTY_LEVELS = {
    "Новичок": {"min_spent": 0, "cashback_percent": 5},
    "Любитель": {"min_spent": 10000, "cashback_percent": 7},
    "Знаток": {"min_spent": 30000, "cashback_percent": 10},
    "Мастер": {"min_spent": 50000, "cashback_percent": 15}
}

# Бонусы за реферальную программу
REFERRAL_BONUS_POINTS = 100
REFERRAL_BONUS_PERCENT = 5

# Промокоды
PROMO_CODES = {
    "WELCOME10": {"discount_percent": 10, "uses_left": 100, "min_order": 1000},
    "TEAFAN20": {"discount_percent": 20, "uses_left": 50, "min_order": 2000},
    "SUMMER25": {"discount_percent": 25, "uses_left": 30, "min_order": 3000}
}

# Категории чая
TEA_CATEGORIES = {
    "black": "Черный чай",
    "green": "Зеленый чай",
    "oolong": "Улун",
    "herbal": "Травяной чай",
    "mate": "Мате",
    "white": "Белый чай"
}

# Товары
TEA_PRODUCTS = {
    "black": [
        {"id": "b1", "name": "Ассам", "description": "Классический индийский черный чай с пряным ароматом.", "price": 450},
        {"id": "b2", "name": "Эрл Грей", "description": "Черный чай с ароматом бергамота.", "price": 500},
        {"id": "b3", "name": "Дарджилинг", "description": "Изысканный черный чай из предгорий Гималаев.", "price": 600}
    ],
    "green": [
        {"id": "g1", "name": "Сенча", "description": "Традиционный японский зеленый чай с освежающим вкусом.", "price": 550},
        {"id": "g2", "name": "Жасминовый", "description": "Зеленый чай с ароматом жасмина.", "price": 500},
        {"id": "g3", "name": "Лун Цзин", "description": "Премиальный китайский зеленый чай 'Колодец дракона'.", "price": 700}
    ],
    "oolong": [
        {"id": "o1", "name": "Те Гуань Инь", "description": "Знаменитый китайский улун с цветочными нотами.", "price": 800},
        {"id": "o2", "name": "Да Хун Пао", "description": "Изысканный темный улун с утесов Уи.", "price": 900}
    ],
    "herbal": [
        {"id": "h1", "name": "Ромашковый", "description": "Успокаивающий травяной чай из цветков ромашки.", "price": 400},
        {"id": "h2", "name": "Мятный", "description": "Освежающий чай из листьев мяты.", "price": 350},
        {"id": "h3", "name": "Фруктовый сбор", "description": "Яркий напиток из сушеных фруктов и ягод.", "price": 450}
    ],
    "mate": [
        {"id": "m1", "name": "Классический мате", "description": "Традиционный южноамериканский напиток из падуба.", "price": 550},
        {"id": "m2", "name": "Мате с лимоном", "description": "Мате с ароматом лимона и легкой кислинкой.", "price": 600}
    ],
    "white": [
        {"id": "w1", "name": "Бай Му Дань", "description": "Белый пион - нежный чай с цветочным ароматом.", "price": 800},
        {"id": "w2", "name": "Серебряные иглы", "description": "Премиальный белый чай из молодых почек.", "price": 1200}
    ]
}

# Заказы
ORDERS = {}

# Корзина пользователей: {user_id: {product_id: {'name': 'Product name', 'price': 100, 'quantity': 2}}}
CART = {}

# Данные для админской сессии: {user_id: {'last_active': datetime, 'session_expires': datetime}}
ADMIN_SESSIONS = {}

# Время действия сессии администратора (24 часа)
ADMIN_SESSION_DURATION = 24 * 60 * 60  # в секундах

# Функции для создания клавиатур
def get_main_menu_keyboard():
    """Создает клавиатуру главного меню"""
    keyboard = [
        [KeyboardButton("🍵 Каталог чая"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("👤 Мой профиль"), KeyboardButton("ℹ️ О магазине")],
        [KeyboardButton("💯 Система лояльности"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команды для админов
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вход в режим администратора"""
    user_id = update.effective_user.id
    
    # Проверяем, является ли пользователь администратором
    if user_id not in ADMIN_IDS:
        await update.message.reply_html(
            "У вас нет прав для доступа к административной панели."
        )
        return
    
    # Проверяем, есть ли активная сессия
    if user_id in ADMIN_SESSIONS and datetime.now() < ADMIN_SESSIONS[user_id]['session_expires']:
        # Сессия активна, сразу показываем админ-панель
        USER_STATES[user_id] = ADMIN_STATE_MAIN
        await show_admin_panel(update, context)
        return
    
    # Запрашиваем пароль
    await update.message.reply_html(
        "Пожалуйста, введите пароль для входа в админ-панель:",
        reply_markup=ForceReply(selective=True)
    )
    
    # Устанавливаем состояние ожидания пароля
    USER_STATES[user_id] = "admin_password"

async def process_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод пароля администратора"""
    password = update.message.text
    user_id = update.effective_user.id
    
    if password != ADMIN_PASSWORD:
        await update.message.reply_html(
            "Неверный пароль. Доступ запрещен."
        )
        USER_STATES[user_id] = STATE_MAIN
        return
    
    # Пароль верный, устанавливаем сессию администратора
    now = datetime.now()
    ADMIN_SESSIONS[user_id] = {
        'last_active': now,
        'session_expires': now + timedelta(seconds=ADMIN_SESSION_DURATION)
    }
    
    # Устанавливаем статус и показываем админ-панель
    USER_STATES[user_id] = ADMIN_STATE_MAIN
    await show_admin_panel(update, context)

# Обновление времени активности админа
def update_admin_activity(user_id):
    """Обновляет время последней активности администратора"""
    if user_id in ADMIN_SESSIONS:
        now = datetime.now()
        ADMIN_SESSIONS[user_id]['last_active'] = now
        # Продлеваем сессию если осталось менее 1 часа
        if ADMIN_SESSIONS[user_id]['session_expires'] - now < timedelta(hours=1):
            ADMIN_SESSIONS[user_id]['session_expires'] = now + timedelta(seconds=ADMIN_SESSION_DURATION)

# Обработчик текстовых команд админ-панели
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения в режиме администратора"""
    text = update.message.text
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return  # Проверка на права админа
    
    # Обновляем время активности администратора
    update_admin_activity(user_id)
    
    state = USER_STATES.get(user_id, "")
    
    # Выход из админ-режима
    if text == "🔙 Выйти из админ-режима":
        USER_STATES[user_id] = STATE_MAIN
        await update.message.reply_html(
            "Вы вышли из режима администратора.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Обработка команд основного меню админ-панели
    if state == ADMIN_STATE_MAIN:
        if text == "📦 Управление заказами":
            USER_STATES[user_id] = ADMIN_STATE_ORDERS
            await show_admin_orders(update, context)
        
        elif text == "🛍️ Управление товарами":
            USER_STATES[user_id] = ADMIN_STATE_PRODUCTS
            await show_admin_products(update, context)
        
        elif text == "💯 Система лояльности":
            USER_STATES[user_id] = ADMIN_STATE_LOYALTY
            await show_admin_loyalty(update, context)
        
        elif text == "🎁 Промокоды":
            USER_STATES[user_id] = ADMIN_STATE_PROMO
            await show_admin_promo(update, context)
        
        elif text == "📊 Статистика":
            USER_STATES[user_id] = ADMIN_STATE_STATS
            await show_admin_stats(update, context)
        
        elif text == "🔄 Обновить данные":
            await update_admin_data(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на инлайн-кнопки"""
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    # Проверяем админские колбэки
    if user_id in ADMIN_IDS and data.startswith("admin_"):
        # Обновляем время активности администратора
        update_admin_activity(user_id)
        
        # Обработка изменения статуса заказа
        if data.startswith("admin_confirm_"):
            order_id = data.replace("admin_confirm_", "")
            await admin_update_order_status(query, order_id, "processing")
            return
        
        elif data.startswith("admin_ship_"):
            order_id = data.replace("admin_ship_", "")
            await admin_update_order_status(query, order_id, "shipped")
            return
        
        elif data.startswith("admin_deliver_"):
            order_id = data.replace("admin_deliver_", "")
            await admin_update_order_status(query, order_id, "delivered")
            return
        
        elif data.startswith("admin_cancel_"):
            order_id = data.replace("admin_cancel_", "")
            await admin_update_order_status(query, order_id, "canceled")
            return
            
        # Вызываем функцию для обработки админских колбэков
        await handle_admin_callback(query, data)
        return
    
    # Проверяем, не находится ли пользователь в админ-режиме
    if user_id in USER_STATES and USER_STATES[user_id].startswith("admin_"):
        await query.answer("Вы в режиме администратора. Сначала выйдите из него для использования функций магазина.", show_alert=True)
        return
        
    # Обработка колбэков для обычных пользователей
    try:
        # Обработка просмотра категорий товаров
        if data.startswith("category_"):
            category_id = data.replace("category_", "")
            # Показать товары выбранной категории
            await show_category_products(query, category_id)
            return
            
        # Обработка просмотра деталей товара
        elif data.startswith("product_"):
            product_id = data.replace("product_", "")
            await show_product_details(query, product_id)
            return
            
        # Обработка добавления товара в корзину
        elif data.startswith("add_to_cart_"):
            product_id = data.replace("add_to_cart_", "")
            await add_to_cart(query, product_id)
            return
            
        # Обработка действий с профилем
        elif data == "profile":
            await show_profile(query)
            return
            
        # Обработка действий с корзиной
        elif data == "cart":
            await show_cart(query)
            return
            
        # Обработка действий с промокодами
        elif data == "promo_codes":
            await show_promo_codes(query)
            return
            
        # Обработка реферальной ссылки
        elif data == "referral_link":
            await get_referral_link(query)
            return
            
        # Обработка возврата в главное меню
        elif data == "main_menu":
            await query.edit_message_text(
                "Главное меню. Выберите действие:",
                reply_markup=get_main_menu_keyboard()
            )
            return
            
        else:
            await query.answer("Неизвестная команда")
            
    except Exception as e:
        # Логируем ошибки и продолжаем работу
        print(f"Ошибка при обработке callback: {e}")
        await query.answer("Произошла ошибка. Попробуйте еще раз.")
        return

async def admin_show_categories_callback(query):
    """Показывает список категорий через callback"""
    buttons = []
    
    # Добавляем кнопки для каждой категории
    for key, name in TEA_CATEGORIES.items():
        buttons.append([InlineKeyboardButton(name, callback_data=f"admin_category_{key}")])
    
    # Добавляем кнопку для создания новой категории
    buttons.append([InlineKeyboardButton("➕ Создать категорию", callback_data="admin_create_category")])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_products")])
    
    await query.edit_message_text(
        """
<b>🏷️ Категории товаров</b>

Выберите категорию для управления товарами или создайте новую:
""",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главную административную панель"""
    # Создаем клавиатуру для админ-панели
    keyboard = [
        [KeyboardButton("📦 Управление заказами"), KeyboardButton("🛍️ Управление товарами")],
        [KeyboardButton("💯 Система лояльности"), KeyboardButton("🎁 Промокоды")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("🔄 Обновить данные")],
        [KeyboardButton("🔙 Выйти из админ-режима")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Отправляем приветственное сообщение с обычной клавиатурой
    message = await update.message.reply_html(
        """
<b>👨‍💼 Административная панель TeaShopBot</b>

Выберите раздел для управления:
• 📦 Управление заказами - просмотр и изменение статусов заказов
• 🛍️ Управление товарами - редактирование ассортимента
• 💯 Система лояльности - настройка программы лояльности
• 🎁 Промокоды - управление акциями и скидками
• 📊 Статистика - анализ продаж и активности
• 🔄 Обновить данные - синхронизация с базой данных
• 🔙 Выйти - возврат в обычный режим
""",
        reply_markup=reply_markup
    )
    
    # Отправляем сообщение с инлайн-клавиатурой
    await update.message.reply_html(
        """
<b>👨‍💼 Панель администратора: быстрый доступ</b>

Используйте кнопки ниже для быстрого доступа к функциям администратора:
""",
        reply_markup=get_admin_main_inline_keyboard()
    )

async def show_product_details(query, product_id):
    """Показывает детальную информацию о товаре"""
    user_id = query.from_user.id
    
    # Находим товар в каталоге
    product = None
    category_id = None
    for cat_id, products in TEA_PRODUCTS.items():
        for p in products:
            if p["id"] == product_id:
                product = p
                category_id = cat_id
                break
        if product:
            break
    
    if not product:
        await query.answer("Товар не найден")
        return
    
    # Формируем текст с описанием товара
    name = product.get("name", "Неизвестно")
    description = product.get("description", "Описание отсутствует")
    price = product.get("price", 0)
    
    text = f"""
<b>{name}</b>

{description}

<b>Цена:</b> {price} ₽ за 100 г
"""
    
    # Создаем клавиатуру
    buttons = []
    buttons.append([InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}")])
    buttons.append([InlineKeyboardButton("🔙 Назад к товарам", callback_data=f"category_{category_id}")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    await query.answer()

async def get_referral_link(query):
    """Генерирует и показывает реферальную ссылку"""
    user_id = query.from_user.id
    
    # Получаем объект бота из контекста
    bot_username = "ваш_бот_юзернейм"  # Замените на реальный юзернейм вашего бота
    
    # Создаем реферальную ссылку
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    
    # Считаем статистику
    referrals_count = sum(1 for user_data in LOYALTY.values() if user_data.get('referred_by') == user_id)
    referral_points = sum(user_data.get('referral_bonus', 0) for user_data in LOYALTY.values() if user_data.get('referred_by') == user_id)
    
    await query.edit_message_text(
        f"""
<b>🔗 Ваша реферальная ссылка</b>

Отправьте эту ссылку друзьям и получайте баллы за их покупки!

<code>{ref_link}</code>

<b>Статистика</b>
• Привлечено друзей: {referrals_count}
• Получено баллов: {referral_points}

Вы получаете <b>{REFERRAL_BONUS_POINTS}</b> баллов, когда друг регистрируется по вашей ссылке.
Также вы получаете <b>{REFERRAL_BONUS_PERCENT}%</b> от суммы каждого заказа вашего друга в виде баллов.
""",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")]
        ])
    )
    await query.answer()

# Стандартные команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    
    # Устанавливаем начальное состояние пользователя
    USER_STATES[user_id] = STATE_MAIN
    
    # Проверяем, есть ли реферальный код
    if context.args and len(context.args) > 0:
        ref_code = context.args[0]
        if ref_code.startswith("ref"):
            # Извлекаем ID реферера
            try:
                referrer_id = int(ref_code[3:])
                if referrer_id != user_id and user_id not in LOYALTY:
                    # Регистрируем нового пользователя с реферальным бонусом
                    LOYALTY[user_id] = {
                        'points': REFERRAL_BONUS_POINTS,
                        'level': 'Новичок',
                        'total_spent': 0,
                        'referred_by': referrer_id
                    }
                    
                    # Начисляем бонус рефереру, если он существует
                    if referrer_id in LOYALTY:
                        LOYALTY[referrer_id]['points'] = LOYALTY[referrer_id].get('points', 0) + REFERRAL_BONUS_POINTS
            except:
                pass
    
    # Если пользователя нет в системе лояльности, добавляем его
    if user_id not in LOYALTY:
        LOYALTY[user_id] = {
            'points': 0,
            'level': 'Новичок',
            'total_spent': 0
        }
    
    # Отправляем приветственное сообщение
    await update.message.reply_html(
        f"""
Привет, <b>{name}</b>! 👋

Добро пожаловать в Tea Shop Bot - ваш гид в мире чая! 🍵

Здесь вы можете:
• Просматривать наш ассортимент чая
• Делать заказы с доставкой
• Накапливать баллы лояльности
• Получать персональные рекомендации

Просто используйте кнопки меню внизу для навигации.
        """,
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /help"""
    await update.message.reply_html(
        """
<b>📚 Справка по использованию Tea Shop Bot</b>

<b>Основные команды:</b>
/start - Запустить бота и перейти в главное меню
/help - Показать эту справку
/admin - Доступ к панели администратора (только для админов)

<b>Как сделать заказ:</b>
1. Нажмите "🍵 Каталог чая" в главном меню
2. Выберите категорию и товар
3. Добавьте товары в корзину
4. Перейдите в корзину и нажмите "Оформить заказ"
5. Укажите адрес доставки
6. Подтвердите заказ

<b>Система лояльности:</b>
• За каждые 100 ₽ покупки вы получаете 5 баллов
• 1 балл = 1 ₽ скидки при следующих покупках
• Чем больше вы покупаете, тем выше ваш уровень лояльности и больше привилегий

<b>Промокоды:</b>
• Применяйте промокоды на странице оформления заказа
• Некоторые промокоды имеют ограничение по минимальной сумме заказа
• Следите за нашими акциями, чтобы получать новые промокоды

Если у вас остались вопросы, свяжитесь с нами через раздел "📞 Контакты".
        """,
        reply_markup=get_main_menu_keyboard()
    )

# Функции для обработки действий пользователя

async def show_category_products(query, category_id):
    """Показывает товары из выбранной категории"""
    category_name = TEA_CATEGORIES.get(category_id, "Неизвестная категория")
    products = TEA_PRODUCTS.get(category_id, [])
    
    if not products:
        await query.answer("В этой категории пока нет товаров")
        return
    
    text = f"<b>{category_name}</b>\nВыберите товар:"
    
    buttons = []
    # Добавляем кнопки с товарами
    for product in products:
        buttons.append([InlineKeyboardButton(
            f"{product['name']} - {product['price']} ₽", 
            callback_data=f"product_{product['id']}"
        )])
    
    # Добавляем кнопку "Назад к категориям"
    buttons.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def add_to_cart(query, product_id):
    """Добавляет товар в корзину пользователя"""
    user_id = query.from_user.id
    
    # Находим товар
    product = None
    for products in TEA_PRODUCTS.values():
        for p in products:
            if p["id"] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        await query.answer("Товар не найден")
        return
    
    # Инициализируем корзину, если её нет
    if user_id not in CART:
        CART[user_id] = {}
    
    # Добавляем или увеличиваем количество товара в корзине
    if product_id in CART[user_id]:
        CART[user_id][product_id]["quantity"] += 1
    else:
        CART[user_id][product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        }
    
    await query.answer(f"Товар {product['name']} добавлен в корзину")

async def show_cart(query):
    """Показывает корзину пользователя"""
    user_id = query.from_user.id
    
    if user_id not in CART or not CART[user_id]:
        await query.edit_message_text(
            "Ваша корзина пуста. Добавьте товары из каталога.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Перейти в каталог", callback_data="main_menu")]
            ])
        )
        return
    
    # Подсчитываем итоговую сумму
    total = sum(item["price"] * item["quantity"] for item in CART[user_id].values())
    
    # Формируем текст корзины
    text = "<b>🛒 Ваша корзина:</b>\n\n"
    for product_id, item in CART[user_id].items():
        text += f"• {item['name']} - {item['price']} ₽ x {item['quantity']} = {item['price'] * item['quantity']} ₽\n"
    
    text += f"\n<b>Итого:</b> {total} ₽"
    
    # Кнопки управления корзиной
    buttons = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🧹 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("🛍️ Продолжить покупки", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def show_profile(query):
    """Показывает профиль пользователя с информацией о лояльности"""
    user_id = query.from_user.id
    
    # Получаем информацию о лояльности
    loyalty_data = LOYALTY.get(user_id, {"points": 0, "level": "Новичок", "total_spent": 0})
    points = loyalty_data.get("points", 0)
    level = loyalty_data.get("level", "Новичок")
    total_spent = loyalty_data.get("total_spent", 0)
    
    # Расчет до следующего уровня
    current_level_info = LOYALTY_LEVELS.get(level, {"min_spent": 0})
    next_level = None
    spent_needed = 0
    
    # Находим следующий уровень
    levels = ["Новичок", "Любитель", "Знаток", "Мастер"]
    current_index = levels.index(level)
    
    if current_index < len(levels) - 1:
        next_level = levels[current_index + 1]
        next_level_info = LOYALTY_LEVELS.get(next_level, {"min_spent": 0})
        spent_needed = next_level_info["min_spent"] - total_spent
    
    text = f"""
<b>👤 Ваш профиль</b>

<b>Уровень лояльности:</b> {level}
<b>Баллы лояльности:</b> {points}
<b>Общая сумма покупок:</b> {total_spent} ₽

"""
    
    if next_level:
        text += f"<b>До уровня {next_level}:</b> {spent_needed} ₽\n"
    
    # Информация о кешбэке
    cashback_percent = LOYALTY_LEVELS.get(level, {}).get("cashback_percent", 0)
    text += f"\n<b>Ваш кешбэк:</b> {cashback_percent}% от суммы заказа"
    
    buttons = [
        [InlineKeyboardButton("🔗 Получить реферальную ссылку", callback_data="referral_link")],
        [InlineKeyboardButton("🎁 Мои промокоды", callback_data="promo_codes")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def show_promo_codes(query):
    """Показывает доступные промокоды пользователя"""
    text = """
<b>🎁 Доступные промокоды</b>

• <code>WELCOME10</code> — скидка 10% на заказ от 1000 ₽
• <code>TEAFAN20</code> — скидка 20% на заказ от 2000 ₽
• <code>SUMMER25</code> — скидка 25% на заказ от 3000 ₽

Введите промокод при оформлении заказа, чтобы получить скидку.
"""
    
    buttons = [
        [InlineKeyboardButton("🔙 Вернуться в профиль", callback_data="profile")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

# Функция для создания инлайн-клавиатуры главного меню
def get_main_inline_keyboard():
    """Создает инлайн-клавиатуру для главного меню"""
    buttons = [
        [InlineKeyboardButton("🍵 Каталог чая", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
    ]
    return InlineKeyboardMarkup(buttons)

# Создание админских инлайн-клавиатур
def get_admin_main_inline_keyboard():
    """Создает инлайн-клавиатуру для главной админ-панели"""
    buttons = [
        [InlineKeyboardButton("📦 Управление заказами", callback_data="admin_orders")],
        [InlineKeyboardButton("🛍️ Управление товарами", callback_data="admin_products")],
        [InlineKeyboardButton("💯 Система лояльности", callback_data="admin_loyalty")],
        [InlineKeyboardButton("🎁 Промокоды", callback_data="admin_promo")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_orders_inline_keyboard():
    """Создает инлайн-клавиатуру для раздела управления заказами"""
    buttons = [
        [InlineKeyboardButton("📋 Новые заказы", callback_data="admin_orders_new")],
        [InlineKeyboardButton("⏳ В обработке", callback_data="admin_orders_processing")],
        [InlineKeyboardButton("🚚 В доставке", callback_data="admin_orders_shipped")],
        [InlineKeyboardButton("✅ Выполненные", callback_data="admin_orders_delivered")],
        [InlineKeyboardButton("❌ Отмененные", callback_data="admin_orders_canceled")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_products_inline_keyboard():
    """Создает инлайн-клавиатуру для раздела управления товарами"""
    buttons = [
        [InlineKeyboardButton("➕ Добавить товар", callback_data="admin_add_product")],
        [InlineKeyboardButton("🏷️ Категории", callback_data="admin_categories")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_loyalty_inline_keyboard():
    """Создает инлайн-клавиатуру для раздела управления системой лояльности"""
    buttons = [
        [InlineKeyboardButton("⚙️ Настройки лояльности", callback_data="admin_loyalty_settings")],
        [InlineKeyboardButton("👥 Топ пользователей", callback_data="admin_loyalty_top_users")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_promo_inline_keyboard():
    """Создает инлайн-клавиатуру для раздела управления промокодами"""
    buttons = [
        [InlineKeyboardButton("➕ Создать промокод", callback_data="admin_add_promo")],
        [InlineKeyboardButton("📊 Статистика использования", callback_data="admin_promo_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_admin_stats_inline_keyboard():
    """Создает инлайн-клавиатуру для раздела статистики"""
    buttons = [
        [InlineKeyboardButton("📅 За сегодня", callback_data="admin_stats_today"), 
         InlineKeyboardButton("📅 За неделю", callback_data="admin_stats_week")],
        [InlineKeyboardButton("📅 За месяц", callback_data="admin_stats_month"), 
         InlineKeyboardButton("📅 За всё время", callback_data="admin_stats_all")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(buttons)

# Обновленные функции для обработки админских callback-запросов
async def handle_admin_callback(query, data):
    """Обрабатывает callback-запросы из админ-панели"""
    user_id = query.from_user.id
    
    # Переход в главное меню админки
    if data == "admin_main":
        await query.edit_message_text(
            """
<b>👨‍💼 Административная панель TeaShopBot</b>

Выберите раздел для управления:
""",
            parse_mode='HTML',
            reply_markup=get_admin_main_inline_keyboard()
        )
    
    # Управление заказами
    elif data == "admin_orders":
        # Считаем количество заказов в разных статусах
        new_orders = len([o for o in ORDERS.values() if o['status'] == 'new'])
        processing_orders = len([o for o in ORDERS.values() if o['status'] == 'processing'])
        shipped_orders = len([o for o in ORDERS.values() if o['status'] == 'shipped'])
        delivered_orders = len([o for o in ORDERS.values() if o['status'] == 'delivered'])
        canceled_orders = len([o for o in ORDERS.values() if o['status'] == 'canceled'])
        
        await query.edit_message_text(
            f"""
<b>📦 Управление заказами</b>

Текущее состояние:
• Новых заказов: <b>{new_orders}</b>
• В обработке: <b>{processing_orders}</b>
• Отправлено: <b>{shipped_orders}</b>
• Доставлено: <b>{delivered_orders}</b>
• Отменено: <b>{canceled_orders}</b>

Выберите категорию заказов:
""",
            parse_mode='HTML',
            reply_markup=get_admin_orders_inline_keyboard()
        )
    
    # Управление товарами
    elif data == "admin_products":
        # Считаем общее количество товаров
        total_products = sum(len(products) for products in TEA_PRODUCTS.values())
        
        await query.edit_message_text(
            f"""
<b>🛍️ Управление товарами</b>

В каталоге: <b>{total_products}</b> товаров в <b>{len(TEA_CATEGORIES)}</b> категориях.

Выберите действие:
""",
            parse_mode='HTML',
            reply_markup=get_admin_products_inline_keyboard()
        )
    
    # Управление системой лояльности
    elif data == "admin_loyalty":
        # Собираем информацию о системе лояльности
        total_users = len(LOYALTY)
        total_points = sum(user_data.get('points', 0) for user_data in LOYALTY.values())
        
        await query.edit_message_text(
            f"""
<b>💯 Управление системой лояльности</b>

Статистика:
• Пользователей в программе: <b>{total_users}</b>
• Всего начислено баллов: <b>{total_points}</b>
• Текущие настройки кэшбэка: от <b>{LOYALTY_LEVELS['Новичок']['cashback_percent']}%</b> до <b>{LOYALTY_LEVELS['Мастер']['cashback_percent']}%</b>
• Реферальный бонус: <b>{REFERRAL_BONUS_POINTS}</b> баллов
• Кэшбэк с рефералов: <b>{REFERRAL_BONUS_PERCENT}%</b>

Выберите действие:
""",
            parse_mode='HTML',
            reply_markup=get_admin_loyalty_inline_keyboard()
        )
    
    # Управление промокодами
    elif data == "admin_promo":
        # Подсчет активных промокодов
        active_promos = sum(1 for promo in PROMO_CODES.values() if promo['uses_left'] > 0)
        
        await query.edit_message_text(
            f"""
<b>🎁 Управление промокодами</b>

Текущее состояние:
• Всего промокодов: <b>{len(PROMO_CODES)}</b>
• Активных промокодов: <b>{active_promos}</b>

Выберите действие:
""",
            parse_mode='HTML',
            reply_markup=get_admin_promo_inline_keyboard()
        )
    
    # Статистика
    elif data == "admin_stats":
        # Собираем основную статистику
        total_orders = len(ORDERS)
        total_revenue = sum(order.get('total', 0) for order in ORDERS.values())
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        
        await query.edit_message_text(
            f"""
<b>📊 Статистика магазина</b>

Общая статистика:
• Всего заказов: <b>{total_orders}</b>
• Общая выручка: <b>{total_revenue} ₽</b>
• Средний чек: <b>{avg_order:.2f} ₽</b>
• Зарегистрировано пользователей: <b>{len(LOYALTY)}</b>

Выберите период для детального анализа:
""",
            parse_mode='HTML',
            reply_markup=get_admin_stats_inline_keyboard()
        )
    
    # Просмотр деталей заказа
    elif data.startswith("admin_order_"):
        order_id = data.replace("admin_order_", "")
        await admin_view_order_callback(query, order_id)
    
    # Просмотр статистики за период
    elif data.startswith("admin_stats_"):
        period = data.replace("admin_stats_", "")
        await show_sales_period_stats_callback(query, period)
    
    # Просмотр заказов по статусу
    elif data.startswith("admin_orders_"):
        status = data.replace("admin_orders_", "")
        await show_orders_by_status_callback(query, status)
    
    # Управление категориями
    elif data == "admin_categories":
        await admin_show_categories_callback(query)
    
    # Создание новой категории
    elif data == "admin_create_category":
        await admin_create_category(query)
    
    # Управление товарами категории
    elif data.startswith("admin_category_"):
        category_key = data.replace("admin_category_", "")
        await admin_select_product_category(query, category_key)
    
    # Переход к добавлению товара
    elif data == "admin_add_product":
        await admin_add_product_callback(query)
    
    # Отмена добавления изображения
    elif data == "admin_skip_image":
        await skip_product_image(query, context=None)
    
    # Прочие callback-запросы
    else:
        await query.answer("Функция находится в разработке")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Проверяем состояние пользователя
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        
        # Обработка админских состояний
        if user_id in ADMIN_IDS:
            # Проверка сессии администратора
            if user_id in ADMIN_SESSIONS:
                now = datetime.now()
                if now > ADMIN_SESSIONS[user_id]['session_expires']:
                    # Сессия истекла
                    USER_STATES[user_id] = STATE_MAIN
                    await update.message.reply_html(
                        "Ваша сессия администратора истекла. Пожалуйста, авторизуйтесь снова с помощью команды /admin",
                        reply_markup=get_main_menu_keyboard()
                    )
                    return
                
                # Обновляем время активности
                update_admin_activity(user_id)
            
            # Проверка ввода пароля для админ-панели
            if state == "admin_password":
                await process_admin_password(update, context)
                return
            
            # Обработка действий админа в зависимости от состояния
            if state.startswith("admin_"):
                if text == "🔙 Выйти из админ-режима":
                    USER_STATES[user_id] = STATE_MAIN
                    await update.message.reply_html(
                        "Вы вышли из режима администратора.",
                        reply_markup=get_main_menu_keyboard()
                    )
                    return
                elif text == "🔙 Назад в админ-меню":
                    USER_STATES[user_id] = ADMIN_STATE_MAIN
                    await show_admin_panel(update, context)
                    return
                
                # Обработка состояний админ-панели
                if state == ADMIN_STATE_MAIN:
                    await handle_admin_text(update, context)
                    return
                elif state == ADMIN_STATE_ORDERS:
                    if text == "📋 Новые заказы":
                        await show_orders_by_status(update, context, "new")
                    elif text == "🚚 Заказы в доставке":
                        await show_orders_by_status(update, context, "shipped")
                    elif text == "✅ Выполненные заказы":
                        await show_orders_by_status(update, context, "delivered")
                    elif text == "❌ Отмененные заказы":
                        await show_orders_by_status(update, context, "canceled")
                    return
                elif state == ADMIN_STATE_PRODUCTS:
                    if text == "➕ Добавить товар":
                        await admin_add_product(update, context)
                    elif text == "🏷️ Категории":
                        await admin_show_categories(update, context)
                    return
                elif state == ADMIN_STATE_LOYALTY:
                    # Обработка команд управления лояльностью
                    pass
                elif state == ADMIN_STATE_STATS:
                    if text == "📅 За сегодня":
                        await show_sales_period_stats(update, context, "today")
                    elif text == "📅 За неделю":
                        await show_sales_period_stats(update, context, "week")
                    elif text == "📅 За месяц":
                        await show_sales_period_stats(update, context, "month")
                    elif text == "📅 За всё время":
                        await show_sales_period_stats(update, context, "all")
                    return
                elif state == ADMIN_STATE_AWAITING_PRODUCT_DATA:
                    await process_new_product_data(update, context)
                    return
                
                # Если сообщение не обработано в admin-режиме, отправляем напоминание
                await update.message.reply_html(
                    "Вы находитесь в режиме администратора. Используйте кнопки на панели или введите команду /admin для возврата в главное меню администратора.",
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Выйти из админ-режима")], [KeyboardButton("🔙 Назад в админ-меню")]], resize_keyboard=True)
                )
                return
        
        # Обработка обычных состояний пользователя
        if state == STATE_AWAITING_ADDRESS:
            # Обрабатываем ввод адреса
            await process_address_input(update, context)
            return
        
        if state == STATE_AWAITING_COMMENT:
            # Обрабатываем ввод комментария
            await process_comment_input(update, context)
            return
        
        if state == STATE_AWAITING_PROMO:
            # Обрабатываем ввод промокода
            await process_promo_code(update, context)
            return
            
        if state == STATE_AWAITING_NAME:
            # Обрабатываем ввод имени
            await process_name_input(update, context)
            return
    
    # Проверяем, не находится ли пользователь в админ-режиме
    if user_id in USER_STATES and USER_STATES[user_id].startswith("admin_"):
        await update.message.reply_html(
            "Вы находитесь в режиме администратора. Чтобы использовать обычные функции бота, сначала выйдите из режима администратора.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Выйти из админ-режима")], [KeyboardButton("🔙 Назад в админ-меню")]], resize_keyboard=True)
        )
        return
        
    # Обработка обычных команд и текста от пользователя
    try:
        # Обработка команд основного меню
        if text == "🍵 Каталог чая":
            await show_catalog(update, context)
        elif text == "🛒 Корзина":
            await show_user_cart(update, context)
        elif text == "👤 Мой профиль":
            await show_user_profile(update, context)
        elif text == "ℹ️ О магазине":
            await show_about(update, context)
        elif text == "💯 Система лояльности":
            await show_loyalty_info(update, context)
        elif text == "📞 Контакты":
            await show_contacts(update, context)
        else:
            # Если не распознали команду, отправляем подсказку
            await update.message.reply_html(
                "Не совсем понимаю, что вы имеете в виду. Воспользуйтесь кнопками меню для управления ботом.",
                reply_markup=get_main_menu_keyboard()
            )
    except Exception as e:
        print(f"Ошибка при обработке текстового сообщения: {e}")
        await update.message.reply_html(
            "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз или воспользуйтесь кнопками меню.",
            reply_markup=get_main_menu_keyboard()
        )

# Функция main для запуска бота
def main():
    """Запускает бота"""
    # Импортируем необходимые компоненты
    import logging
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
    import os
    
    # Настраиваем логирование
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    # Получаем токен бота
    TOKEN = os.environ.get("TELEGRAM_TOKEN", "7638208338:AAElrmQU861HX70ZQVRUY5gLUYHabK3y0qg")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Регистрируем обработчик callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Запускаем бота
    logger.info("Бот запущен")
    print("Бот запущен. Чтобы остановить, нажмите Ctrl+C")
    application.run_polling()

if __name__ == "__main__":
    main()

async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает каталог категорий чая"""
    # Создаем инлайн клавиатуру с категориями
    buttons = []
    for category_id, category_name in TEA_CATEGORIES.items():
        buttons.append([InlineKeyboardButton(category_name, callback_data=f"category_{category_id}")])
    
    # Добавляем кнопку возврата в главное меню
    buttons.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_html(
        "<b>🍵 Каталог чая</b>\n\nВыберите категорию:",
        reply_markup=keyboard
    )

async def show_user_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает корзину пользователя через текстовое сообщение"""
    user_id = update.effective_user.id
    
    if user_id not in CART or not CART[user_id]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Перейти в каталог", callback_data="catalog")]
        ])
        
        await update.message.reply_html(
            "Ваша корзина пуста. Добавьте товары из каталога.",
            reply_markup=keyboard
        )
        return
    
    # Подсчитываем итоговую сумму
    total = sum(item["price"] * item["quantity"] for item in CART[user_id].values())
    
    # Формируем текст корзины
    text = "<b>🛒 Ваша корзина:</b>\n\n"
    for product_id, item in CART[user_id].items():
        text += f"• {item['name']} - {item['price']} ₽ x {item['quantity']} = {item['price'] * item['quantity']} ₽\n"
    
    text += f"\n<b>Итого:</b> {total} ₽"
    
    # Кнопки управления корзиной
    buttons = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🧹 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("🛍️ Продолжить покупки", callback_data="catalog")]
    ]
    
    await update.message.reply_html(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает профиль пользователя через текстовое сообщение"""
    user_id = update.effective_user.id
    
    # Получаем информацию о лояльности
    loyalty_data = LOYALTY.get(user_id, {"points": 0, "level": "Новичок", "total_spent": 0})
    points = loyalty_data.get("points", 0)
    level = loyalty_data.get("level", "Новичок")
    total_spent = loyalty_data.get("total_spent", 0)
    
    # Расчет до следующего уровня
    next_level = None
    spent_needed = 0
    
    # Находим следующий уровень
    levels = ["Новичок", "Любитель", "Знаток", "Мастер"]
    current_index = levels.index(level)
    
    if current_index < len(levels) - 1:
        next_level = levels[current_index + 1]
        next_level_info = LOYALTY_LEVELS.get(next_level, {"min_spent": 0})
        spent_needed = next_level_info["min_spent"] - total_spent
    
    text = f"""
<b>👤 Ваш профиль</b>

<b>Уровень лояльности:</b> {level}
<b>Баллы лояльности:</b> {points}
<b>Общая сумма покупок:</b> {total_spent} ₽

"""
    
    if next_level:
        text += f"<b>До уровня {next_level}:</b> {spent_needed} ₽\n"
    
    # Информация о кешбэке
    cashback_percent = LOYALTY_LEVELS.get(level, {}).get("cashback_percent", 0)
    text += f"\n<b>Ваш кешбэк:</b> {cashback_percent}% от суммы заказа"
    
    buttons = [
        [InlineKeyboardButton("🔗 Получить реферальную ссылку", callback_data="referral_link")],
        [InlineKeyboardButton("🎁 Мои промокоды", callback_data="promo_codes")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    
    await update.message.reply_html(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о магазине"""
    await update.message.reply_html(
        """
<b>ℹ️ О магазине</b>

<b>Tea Shop Bot</b> — это виртуальный магазин элитных сортов чая со всего мира.

<b>Наши преимущества:</b>
• Прямые поставки из чайных регионов
• Строгий контроль качества продукции
• Подробные описания и рекомендации
• Быстрая доставка по всей стране
• Программа лояльности для постоянных клиентов

<b>История магазина:</b>
Наш магазин основан в 2020 году группой энтузиастов чайной культуры с целью сделать доступными редкие и качественные сорта чая для ценителей этого благородного напитка.

Мы регулярно пополняем ассортимент и следим за тенденциями чайного рынка, чтобы предложить вам только лучшее.
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ])
    )

async def show_loyalty_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о системе лояльности"""
    await update.message.reply_html(
        f"""
<b>💯 Система лояльности Tea Shop Bot</b>

Накапливайте баллы и получайте привилегии!

<b>Как это работает:</b>
• За каждые 100 ₽ покупки вы получаете 5 баллов
• 1 балл = 1 ₽ скидки при следующих покупках
• Чем больше покупаете, тем выше уровень и больше привилегий

<b>Уровни лояльности:</b>
• <b>Новичок</b> (0-{LOYALTY_LEVELS['Любитель']['min_spent']-1} ₽): кешбэк {LOYALTY_LEVELS['Новичок']['cashback_percent']}%
• <b>Любитель</b> ({LOYALTY_LEVELS['Любитель']['min_spent']}-{LOYALTY_LEVELS['Знаток']['min_spent']-1} ₽): кешбэк {LOYALTY_LEVELS['Любитель']['cashback_percent']}%
• <b>Знаток</b> ({LOYALTY_LEVELS['Знаток']['min_spent']}-{LOYALTY_LEVELS['Мастер']['min_spent']-1} ₽): кешбэк {LOYALTY_LEVELS['Знаток']['cashback_percent']}%
• <b>Мастер</b> (от {LOYALTY_LEVELS['Мастер']['min_spent']} ₽): кешбэк {LOYALTY_LEVELS['Мастер']['cashback_percent']}%

<b>Реферальная программа:</b>
• Вы получаете {REFERRAL_BONUS_POINTS} баллов за каждого приглашенного друга
• Дополнительно {REFERRAL_BONUS_PERCENT}% от суммы заказов ваших друзей в виде баллов
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 Посмотреть свой профиль", callback_data="profile")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ])
    )

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает контактную информацию"""
    await update.message.reply_html(
        """
<b>📞 Контакты</b>

<b>Телефон:</b> +7 (800) 123-45-67
<b>Email:</b> support@teashopbot.com
<b>График работы:</b> Пн-Пт с 9:00 до 20:00, Сб-Вс с 10:00 до 18:00

<b>Социальные сети:</b>
• Telegram: @teashopbot
• Instagram: @teashop_official
• VK: vk.com/teashop

<b>Адрес офиса:</b>
г. Москва, ул. Чайная, д. 15, офис 42

По всем вопросам и предложениям обращайтесь в нашу службу поддержки. Мы ответим вам в течение 24 часов.
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✉️ Написать в поддержку", url="https://t.me/teashopbot")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ])
    )

# Функции админки для работы с заказами и статистикой
async def show_admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает раздел управления заказами в админке"""
    # Создаем клавиатуру для выбора статуса заказов
    keyboard = [
        [KeyboardButton("📋 Новые заказы"), KeyboardButton("⏳ В обработке")],
        [KeyboardButton("🚚 Заказы в доставке"), KeyboardButton("✅ Выполненные заказы")],
        [KeyboardButton("❌ Отмененные заказы")],
        [KeyboardButton("🔙 Назад в админ-меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Считаем количество заказов в разных статусах
    new_orders = len([o for o in ORDERS.values() if o.get('status') == 'new'])
    processing_orders = len([o for o in ORDERS.values() if o.get('status') == 'processing'])
    shipped_orders = len([o for o in ORDERS.values() if o.get('status') == 'shipped'])
    delivered_orders = len([o for o in ORDERS.values() if o.get('status') == 'delivered'])
    canceled_orders = len([o for o in ORDERS.values() if o.get('status') == 'canceled'])
    
    await update.message.reply_html(
        f"""
<b>📦 Управление заказами</b>

Текущее состояние:
• Новых заказов: <b>{new_orders}</b>
• В обработке: <b>{processing_orders}</b>
• Отправлено: <b>{shipped_orders}</b>
• Доставлено: <b>{delivered_orders}</b>
• Отменено: <b>{canceled_orders}</b>

Выберите категорию заказов для просмотра:
""",
        reply_markup=reply_markup
    )

async def show_admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает раздел управления товарами в админке"""
    # Создаем клавиатуру для управления товарами
    keyboard = [
        [KeyboardButton("➕ Добавить товар"), KeyboardButton("🏷️ Категории")],
        [KeyboardButton("🔙 Назад в админ-меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Считаем общее количество товаров
    total_products = sum(len(products) for products in TEA_PRODUCTS.values())
    
    await update.message.reply_html(
        f"""
<b>🛍️ Управление товарами</b>

Текущее состояние:
• Всего товаров: <b>{total_products}</b>
• Категорий: <b>{len(TEA_CATEGORIES)}</b>

Выберите действие:
""",
        reply_markup=reply_markup
    )

async def show_admin_loyalty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает раздел управления системой лояльности в админке"""
    # Создаем клавиатуру для управления лояльностью
    keyboard = [
        [KeyboardButton("⚙️ Настройки лояльности"), KeyboardButton("👥 Топ пользователей")],
        [KeyboardButton("🔙 Назад в админ-меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Собираем информацию о системе лояльности
    total_users = len(LOYALTY)
    total_points = sum(user_data.get('points', 0) for user_data in LOYALTY.values())
    
    await update.message.reply_html(
        f"""
<b>💯 Управление системой лояльности</b>

Текущее состояние:
• Пользователей в программе: <b>{total_users}</b>
• Всего начислено баллов: <b>{total_points}</b>
• Кешбэк: от <b>{LOYALTY_LEVELS['Новичок']['cashback_percent']}%</b> до <b>{LOYALTY_LEVELS['Мастер']['cashback_percent']}%</b>
• Реферальный бонус: <b>{REFERRAL_BONUS_POINTS}</b> баллов
• Кэшбэк с рефералов: <b>{REFERRAL_BONUS_PERCENT}%</b>

Выберите действие:
""",
        reply_markup=reply_markup
    )

async def show_admin_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает раздел управления промокодами в админке"""
    # Создаем клавиатуру для управления промокодами
    keyboard = [
        [KeyboardButton("➕ Создать промокод"), KeyboardButton("📊 Статистика использования")],
        [KeyboardButton("🔙 Назад в админ-меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Подсчет активных промокодов
    active_promos = sum(1 for promo in PROMO_CODES.values() if promo['uses_left'] > 0)
    
    await update.message.reply_html(
        f"""
<b>🎁 Управление промокодами</b>

Текущее состояние:
• Всего промокодов: <b>{len(PROMO_CODES)}</b>
• Активных промокодов: <b>{active_promos}</b>

Выберите действие:
""",
        reply_markup=reply_markup
    )

async def show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает раздел статистики в админке"""
    # Создаем клавиатуру для выбора периода статистики
    keyboard = [
        [KeyboardButton("📅 За сегодня"), KeyboardButton("📅 За неделю")],
        [KeyboardButton("📅 За месяц"), KeyboardButton("📅 За всё время")],
        [KeyboardButton("🔙 Назад в админ-меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Собираем основную статистику
    total_orders = len(ORDERS)
    total_revenue = sum(order.get('total', 0) for order in ORDERS.values())
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    
    await update.message.reply_html(
        f"""
<b>📊 Статистика магазина</b>

Общая статистика:
• Всего заказов: <b>{total_orders}</b>
• Общая выручка: <b>{total_revenue} ₽</b>
• Средний чек: <b>{avg_order:.2f} ₽</b>
• Зарегистрировано пользователей: <b>{len(LOYALTY)}</b>

Выберите период для детального анализа:
""",
        reply_markup=reply_markup
    )

async def update_admin_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновляет данные админки"""
    await update.message.reply_html(
        """
<b>🔄 Данные успешно обновлены</b>

Обновлена информация о:
• Заказах
• Товарах
• Пользователях
• Статистике
""",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("🔙 Назад в админ-меню")]
        ], resize_keyboard=True)
    )

async def show_orders_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE, status):
    """Показывает список заказов с определенным статусом"""
    # Фильтруем заказы по статусу
    filtered_orders = {order_id: order for order_id, order in ORDERS.items() if order.get('status') == status}
    
    if not filtered_orders:
        await update.message.reply_html(
            f"В настоящее время нет заказов со статусом '{status}'",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("🔙 Назад в админ-меню")]
            ], resize_keyboard=True)
        )
        return
    
    # Создаем текст со списком заказов
    text = f"<b>Заказы со статусом '{status}':</b>\n\n"
    
    for order_id, order in filtered_orders.items():
        # Формируем строку с краткой информацией о заказе
        date = order.get('date', 'Неизвестно')
        user_id = order.get('user_id', 'Неизвестно')
        total = order.get('total', 0)
        
        text += f"📦 <b>Заказ #{order_id}</b>\n"
        text += f"Дата: {date}\n"
        text += f"Пользователь: {user_id}\n"
        text += f"Сумма: {total} ₽\n\n"
    
    # Создаем инлайн-клавиатуру для просмотра деталей заказов
    buttons = []
    for order_id in filtered_orders.keys():
        buttons.append([InlineKeyboardButton(f"Заказ #{order_id}", callback_data=f"admin_order_{order_id}")])
    
    await update.message.reply_html(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def admin_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает процесс добавления нового товара"""
    user_id = update.effective_user.id
    USER_STATES[user_id] = ADMIN_STATE_AWAITING_PRODUCT_DATA
    
    await update.message.reply_html(
        """
<b>➕ Добавление нового товара</b>

Введите данные о товаре в формате:
<code>категория;название;описание;цена</code>

Например:
<code>black;Кенийский чай;Крепкий черный чай из Кении;500</code>

Категории:
• black - Черный чай
• green - Зеленый чай
• oolong - Улун
• herbal - Травяной чай
• mate - Мате
• white - Белый чай
""",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("🔙 Назад")]
        ], resize_keyboard=True)
    )

async def admin_show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список категорий товаров"""
    buttons = []
    
    # Добавляем кнопки для каждой категории
    for key, name in TEA_CATEGORIES.items():
        buttons.append([InlineKeyboardButton(name, callback_data=f"admin_category_{key}")])
    
    # Добавляем кнопку для создания новой категории
    buttons.append([InlineKeyboardButton("➕ Создать категорию", callback_data="admin_create_category")])
    
    await update.message.reply_html(
        """
<b>🏷️ Категории товаров</b>

Выберите категорию для управления товарами или создайте новую:
""",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def admin_view_order_callback(query, order_id):
    """Показывает детали заказа и кнопки управления статусом"""
    # Находим заказ
    order = ORDERS.get(order_id)
    
    if not order:
        await query.answer("Заказ не найден")
        return
    
    # Получаем данные заказа
    status = order.get('status', 'new')
    date = order.get('date', 'Неизвестно')
    user_id = order.get('user_id', 'Неизвестно')
    total = order.get('total', 0)
    address = order.get('address', 'Не указан')
    items = order.get('items', {})
    
    # Формируем детальный текст заказа
    text = f"""
<b>📦 Заказ #{order_id}</b>

<b>Статус:</b> {status.upper()}
<b>Дата:</b> {date}
<b>ID пользователя:</b> {user_id}
<b>Адрес доставки:</b> {address}

<b>Товары:</b>
"""
    
    for item_id, item_data in items.items():
        name = item_data.get('name', 'Неизвестно')
        quantity = item_data.get('quantity', 0)
        price = item_data.get('price', 0)
        text += f"• {name} x {quantity} = {price * quantity} ₽\n"
    
    text += f"\n<b>Итого:</b> {total} ₽"
    
    # Создаем клавиатуру с кнопками изменения статуса
    buttons = []
    
    if status == 'new':
        buttons.append([InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"admin_confirm_{order_id}")])
        buttons.append([InlineKeyboardButton("❌ Отменить заказ", callback_data=f"admin_cancel_{order_id}")])
    elif status == 'processing':
        buttons.append([InlineKeyboardButton("🚚 Отправить заказ", callback_data=f"admin_ship_{order_id}")])
        buttons.append([InlineKeyboardButton("❌ Отменить заказ", callback_data=f"admin_cancel_{order_id}")])
    elif status == 'shipped':
        buttons.append([InlineKeyboardButton("✅ Заказ доставлен", callback_data=f"admin_deliver_{order_id}")])
    
    # Добавляем кнопку назад
    if status in ['new', 'processing', 'shipped']:
        buttons.append([InlineKeyboardButton("🔙 Назад к списку", callback_data=f"admin_orders_{status}")])
    else:
        buttons.append([InlineKeyboardButton("🔙 Назад к списку", callback_data=f"admin_orders")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def admin_update_order_status(query, order_id, new_status):
    """Обновляет статус заказа и уведомляет пользователя"""
    # Проверяем, существует ли заказ
    if order_id not in ORDERS:
        await query.answer("Заказ не найден")
        return
    
    # Обновляем статус
    old_status = ORDERS[order_id].get('status', 'new')
    ORDERS[order_id]['status'] = new_status
    
    # Получаем ID пользователя для отправки уведомления
    user_id = ORDERS[order_id].get('user_id')
    
    # Формируем сообщение статуса для админа
    status_messages = {
        'processing': "✅ Заказ успешно подтвержден и передан в обработку",
        'shipped': "🚚 Заказ отправлен в доставку",
        'delivered': "✅ Заказ доставлен клиенту",
        'canceled': "❌ Заказ отменен"
    }
    
    # Уведомляем админа о смене статуса
    await query.answer(status_messages.get(new_status, f"Статус изменен на: {new_status}"))
    
    # Формируем текст с обновленными данными заказа
    await admin_view_order_callback(query, order_id)
    
    # TODO: Отправить уведомление пользователю о смене статуса заказа
    # Это делается с помощью context.bot.send_message(user_id, текст_сообщения)
    # Но у нас нет доступа к context в этой функции
    
async def show_orders_by_status_callback(query, status):
    """Показывает список заказов через callback"""
    # Фильтруем заказы по статусу
    filtered_orders = {order_id: order for order_id, order in ORDERS.items() if order.get('status') == status}
    
    if not filtered_orders:
        await query.edit_message_text(
            f"В настоящее время нет заказов со статусом '{status}'",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_orders")]
            ])
        )
        await query.answer()
        return
    
    # Создаем текст со списком заказов
    text = f"<b>Заказы со статусом '{status}':</b>\n\n"
    
    for order_id, order in filtered_orders.items():
        # Формируем строку с краткой информацией о заказе
        date = order.get('date', 'Неизвестно')
        user_id = order.get('user_id', 'Неизвестно')
        total = order.get('total', 0)
        
        text += f"📦 <b>Заказ #{order_id}</b>\n"
        text += f"Дата: {date}\n"
        text += f"Пользователь: {user_id}\n"
        text += f"Сумма: {total} ₽\n\n"
    
    # Создаем инлайн-клавиатуру для просмотра деталей заказов
    buttons = []
    for order_id in filtered_orders.keys():
        buttons.append([InlineKeyboardButton(f"Заказ #{order_id}", callback_data=f"admin_order_{order_id}")])
    
    # Добавляем кнопку назад
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_orders")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def show_sales_period_stats_callback(query, period):
    """Показывает статистику продаж за выбранный период"""
    # Определяем начальную дату для фильтрации
    now = datetime.now()
    start_date = None
    
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "сегодня"
    elif period == "week":
        start_date = now - timedelta(days=7)
        period_name = "за неделю"
    elif period == "month":
        start_date = now - timedelta(days=30)
        period_name = "за месяц"
    else:  # all time
        start_date = None
        period_name = "за всё время"
    
    # Фильтруем заказы по дате
    filtered_orders = {}
    if start_date:
        filtered_orders = {
            order_id: order for order_id, order in ORDERS.items() 
            if datetime.fromisoformat(order.get('date', '2020-01-01')) >= start_date
        }
    else:
        filtered_orders = ORDERS
    
    # Подсчитываем статистику
    total_orders = len(filtered_orders)
    total_revenue = sum(order.get('total', 0) for order in filtered_orders.values())
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    
    # Статистика по статусам
    status_counts = {}
    for order in filtered_orders.values():
        status = order.get('status', 'new')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Формируем текст статистики
    text = f"""
<b>📊 Статистика {period_name}</b>

<b>Общая статистика:</b>
• Всего заказов: <b>{total_orders}</b>
• Общая выручка: <b>{total_revenue} ₽</b>
• Средний чек: <b>{avg_order:.2f} ₽</b>

<b>По статусам:</b>
• Новых: <b>{status_counts.get('new', 0)}</b>
• В обработке: <b>{status_counts.get('processing', 0)}</b>
• В доставке: <b>{status_counts.get('shipped', 0)}</b>
• Доставлено: <b>{status_counts.get('delivered', 0)}</b>
• Отменено: <b>{status_counts.get('canceled', 0)}</b>
"""
    
    # Создаем клавиатуру для выбора периода
    buttons = [
        [
            InlineKeyboardButton("📅 За сегодня", callback_data="admin_stats_today"),
            InlineKeyboardButton("📅 За неделю", callback_data="admin_stats_week")
        ],
        [
            InlineKeyboardButton("📅 За месяц", callback_data="admin_stats_month"),
            InlineKeyboardButton("📅 За всё время", callback_data="admin_stats_all")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def admin_create_category(query):
    """Показывает инструкции по созданию новой категории"""
    await query.edit_message_text(
        """
<b>➕ Создание новой категории</b>

Для создания новой категории вам нужно:
1. Выйти из инлайн-режима и отправить текстовое сообщение в формате:
<code>категория_id;Название категории</code>

Например:
<code>puerh;Пуэр</code>

<b>Примечание:</b> ID категории должен быть на английском языке, без пробелов и спецсимволов. Название категории может быть на любом языке.
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад к категориям", callback_data="admin_categories")]
        ]),
        parse_mode='HTML'
    )
    await query.answer()

async def admin_select_product_category(query, category_key):
    """Показывает товары в выбранной категории для управления"""
    # Получаем название категории
    category_name = TEA_CATEGORIES.get(category_key, "Неизвестная категория")
    
    # Получаем товары в этой категории
    products = TEA_PRODUCTS.get(category_key, [])
    
    if not products:
        await query.edit_message_text(
            f"В категории <b>{category_name}</b> пока нет товаров",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить товар", callback_data=f"admin_add_product_to_{category_key}")],
                [InlineKeyboardButton("🔙 Назад к категориям", callback_data="admin_categories")]
            ]),
            parse_mode='HTML'
        )
        await query.answer()
        return
    
    # Создаем текст с товарами
    text = f"<b>Товары в категории '{category_name}':</b>\n\n"
    
    for product in products:
        product_id = product.get('id', '')
        name = product.get('name', 'Неизвестно')
        price = product.get('price', 0)
        
        text += f"• <b>{name}</b> - {price} ₽\n"
    
    # Создаем клавиатуру с кнопками управления товарами
    buttons = []
    for product in products:
        product_id = product.get('id', '')
        name = product.get('name', '')
        buttons.append([InlineKeyboardButton(f"✏️ {name}", callback_data=f"admin_edit_product_{product_id}")])
    
    # Добавляем кнопку для добавления нового товара
    buttons.append([InlineKeyboardButton("➕ Добавить товар", callback_data=f"admin_add_product_to_{category_key}")])
    
    # Добавляем кнопку назад
    buttons.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="admin_categories")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='HTML'
    )
    await query.answer()

async def admin_add_product_callback(query):
    """Показывает инструкции по добавлению нового товара через callback"""
    await query.edit_message_text(
        """
<b>➕ Добавление нового товара</b>

Для добавления нового товара вам нужно:
1. Выйти из инлайн-режима и отправить текстовое сообщение в формате:
<code>категория;название;описание;цена</code>

Например:
<code>black;Кенийский чай;Крепкий черный чай из Кении;500</code>

Категории:
• black - Черный чай
• green - Зеленый чай
• oolong - Улун
• herbal - Травяной чай
• mate - Мате
• white - Белый чай
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_products")]
        ]),
        parse_mode='HTML'
    )
    await query.answer()

async def process_new_product_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает данные нового товара, введенные администратором"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверяем правильность формата
    if text == "🔙 Назад":
        USER_STATES[user_id] = ADMIN_STATE_PRODUCTS
        await show_admin_products(update, context)
        return
    
    parts = text.strip().split(';')
    if len(parts) != 4:
        await update.message.reply_html(
            """
❌ <b>Ошибка формата</b>

Пожалуйста, введите данные в формате:
<code>категория;название;описание;цена</code>

Например:
<code>black;Кенийский чай;Крепкий черный чай из Кении;500</code>
""",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("🔙 Назад")]
            ], resize_keyboard=True)
        )
        return
    
    category, name, description, price_str = parts
    
    # Проверяем существование категории
    if category not in TEA_CATEGORIES:
        await update.message.reply_html(
            f"""
❌ <b>Категория не найдена</b>

Категория '{category}' не существует. Доступные категории:
• black - Черный чай
• green - Зеленый чай
• oolong - Улун
• herbal - Травяной чай
• mate - Мате
• white - Белый чай
""",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("🔙 Назад")]
            ], resize_keyboard=True)
        )
        return
    
    # Проверяем корректность цены
    try:
        price = int(price_str)
        if price <= 0:
            raise ValueError("Цена должна быть положительным числом")
    except ValueError:
        await update.message.reply_html(
            """
❌ <b>Некорректная цена</b>

Цена должна быть положительным числом.
""",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("🔙 Назад")]
            ], resize_keyboard=True)
        )
        return
    
    # Генерируем уникальный ID для товара
    product_id = f"{category[0]}{len(TEA_PRODUCTS[category]) + 1}"
    
    # Добавляем товар в категорию
    new_product = {
        "id": product_id,
        "name": name,
        "description": description,
        "price": price
    }
    
    TEA_PRODUCTS[category].append(new_product)
    
    # Сообщаем об успешном добавлении товара
    await update.message.reply_html(
        f"""
✅ <b>Товар успешно добавлен</b>

ID: {product_id}
Категория: {TEA_CATEGORIES[category]}
Название: {name}
Цена: {price} ₽
""",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("➕ Добавить еще товар")], 
            [KeyboardButton("🔙 Назад в меню товаров")]
        ], resize_keyboard=True)
    )
    
    # Возвращаем пользователя в меню товаров
    USER_STATES[user_id] = ADMIN_STATE_PRODUCTS