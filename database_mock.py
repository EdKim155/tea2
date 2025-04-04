"""
Эмуляция базы данных для запуска без MongoDB
"""

# Локальное хранилище данных
_users = {}
_orders = {}
_cart = {}

def register_user(user_id, first_name, last_name=None, phone_number=None):
    """Регистрация нового пользователя или обновление данных существующего"""
    user_data = {
        '_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'phone_number': phone_number,
        'registered_at': None  # Будет заполнено при подтверждении телефона
    }
    
    # Обновляем или создаем
    _users[user_id] = {**(_users.get(user_id, {})), **user_data}
    
    return user_data


def update_user_phone(user_id, phone_number, timestamp):
    """Обновление телефона пользователя и установка времени регистрации"""
    if user_id in _users:
        _users[user_id]['phone_number'] = phone_number
        _users[user_id]['registered_at'] = timestamp
        return True
    return False


def get_user(user_id):
    """Получение данных пользователя"""
    return _users.get(user_id)


def is_user_registered(user_id):
    """Проверка, зарегистрирован ли пользователь полностью (с телефоном)"""
    user = get_user(user_id)
    return user and user.get('phone_number') and user.get('registered_at')


def add_to_cart(user_id, product_id, quantity=1):
    """Добавление товара в корзину"""
    # Инициализируем корзину пользователя, если её еще нет
    if user_id not in _cart:
        _cart[user_id] = []
    
    # Проверяем, есть ли уже этот товар в корзине
    found = False
    for item in _cart[user_id]:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            # Удаляем товар, если количество <= 0
            if item['quantity'] <= 0:
                _cart[user_id].remove(item)
            found = True
            break
    
    # Если товара нет и добавляется положительное количество, добавляем новый
    if not found and quantity > 0:
        _cart[user_id].append({
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        })


def get_cart(user_id):
    """Получение содержимого корзины пользователя"""
    return _cart.get(user_id, [])


def clear_cart(user_id):
    """Очистка корзины пользователя"""
    if user_id in _cart:
        _cart[user_id] = []


def create_order(user_id, cart_items, shipping_address, payment_method, timestamp):
    """Создание нового заказа"""
    order_id = f"order_{len(_orders) + 1}"
    
    order = {
        '_id': order_id,
        'user_id': user_id,
        'items': cart_items.copy(),  # Копируем, чтобы избежать проблем при изменении корзины
        'shipping_address': shipping_address,
        'payment_method': payment_method,
        'status': 'new',
        'created_at': timestamp
    }
    
    _orders[order_id] = order
    
    return order_id


def get_user_orders(user_id):
    """Получение истории заказов пользователя"""
    user_orders = [order for order in _orders.values() if order['user_id'] == user_id]
    # Сортируем по дате (новые сначала)
    return sorted(user_orders, key=lambda x: x.get('created_at', ''), reverse=True) 