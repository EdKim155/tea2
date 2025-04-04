from pymongo import MongoClient
from config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_database('tea_shop')

users_collection = db.users
orders_collection = db.orders
cart_collection = db.cart


def register_user(user_id, first_name, last_name=None, phone_number=None):
    """Регистрация нового пользователя или обновление данных существующего"""
    user_data = {
        'first_name': first_name,
        'last_name': last_name,
        'phone_number': phone_number,
        'registered_at': None  # Будет заполнено при подтверждении телефона
    }
    
    # Используем upsert=True для создания нового документа, если пользователя нет
    users_collection.update_one(
        {'_id': user_id}, 
        {'$set': user_data},
        upsert=True
    )
    
    return user_data


def update_user_phone(user_id, phone_number, timestamp):
    """Обновление телефона пользователя и установка времени регистрации"""
    result = users_collection.update_one(
        {'_id': user_id},
        {'$set': {
            'phone_number': phone_number,
            'registered_at': timestamp
        }}
    )
    return result.modified_count > 0


def get_user(user_id):
    """Получение данных пользователя"""
    return users_collection.find_one({'_id': user_id})


def is_user_registered(user_id):
    """Проверка, зарегистрирован ли пользователь полностью (с телефоном)"""
    user = get_user(user_id)
    return user and user.get('phone_number') and user.get('registered_at')


def add_to_cart(user_id, product_id, quantity=1):
    """Добавление товара в корзину"""
    # Проверяем, есть ли уже этот товар в корзине
    cart_item = cart_collection.find_one({
        'user_id': user_id,
        'product_id': product_id
    })
    
    if cart_item:
        # Обновляем количество
        cart_collection.update_one(
            {'_id': cart_item['_id']},
            {'$inc': {'quantity': quantity}}
        )
    else:
        # Добавляем новый товар
        cart_collection.insert_one({
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        })


def get_cart(user_id):
    """Получение содержимого корзины пользователя"""
    return list(cart_collection.find({'user_id': user_id}))


def clear_cart(user_id):
    """Очистка корзины пользователя"""
    cart_collection.delete_many({'user_id': user_id})


def create_order(user_id, cart_items, shipping_address, payment_method, timestamp):
    """Создание нового заказа"""
    order = {
        'user_id': user_id,
        'items': cart_items,
        'shipping_address': shipping_address,
        'payment_method': payment_method,
        'status': 'new',
        'created_at': timestamp
    }
    
    result = orders_collection.insert_one(order)
    return result.inserted_id


def get_user_orders(user_id):
    """Получение истории заказов пользователя"""
    return list(orders_collection.find({'user_id': user_id}).sort('created_at', -1)) 