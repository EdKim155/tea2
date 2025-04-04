import re
from config import TEA_PRODUCTS

def find_product_by_id(product_id):
    """Находит товар по его id"""
    for category, products in TEA_PRODUCTS.items():
        for product in products:
            if product['id'] == product_id:
                return product
    return None

def extract_product_id(callback_data):
    """Извлекает ID товара из callback_data"""
    match = re.search(r'(?:product_|add_to_cart_|remove_|increase_|decrease_)(.+)', callback_data)
    if match:
        return match.group(1)
    return None

def extract_category_key(callback_data):
    """Извлекает ключ категории из callback_data"""
    match = re.search(r'category_(.+)', callback_data)
    if match:
        return match.group(1)
    return None

def format_cart_message(cart_items):
    """Формирует сообщение с содержимым корзины"""
    if not cart_items:
        return "Ваша корзина пуста."
    
    total = 0
    lines = ["<b>🛒 Ваша корзина:</b>\n"]
    
    for i, item in enumerate(cart_items, 1):
        product = find_product_by_id(item['product_id'])
        if product:
            price = product['price']
            item_total = price * item['quantity']
            total += item_total
            
            lines.append(
                f"{i}. <b>{product['name']}</b> x {item['quantity']} = {item_total} ₽"
            )
    
    lines.append(f"\n<b>Итого:</b> {total} ₽")
    
    return "\n".join(lines)

def format_product_details(product):
    """Форматирует детальную информацию о товаре"""
    if not product:
        return "Товар не найден."
    
    return f"""
<b>{product['name']}</b>

{product['description']}

<b>Цена:</b> {product['price']} ₽ за 100 г
"""

def format_order_details(order, items_with_details):
    """Форматирует информацию о заказе"""
    created_at = order.get('created_at', '')
    status = get_order_status_emoji(order.get('status', '')) + " " + get_status_description(order.get('status', ''))
    
    total = 0
    items_text = []
    
    for item in items_with_details:
        product = item.get('product', {})
        quantity = item.get('quantity', 0)
        price = product.get('price', 0)
        item_total = price * quantity
        total += item_total
        
        items_text.append(
            f"• {product.get('name', 'Неизвестный товар')} x {quantity} = {item_total} ₽"
        )
    
    result = f"""
<b>📋 Заказ №{str(order.get('_id', ''))[-6:]}</b>

<b>Дата:</b> {created_at.strftime('%d.%m.%Y %H:%M') if hasattr(created_at, 'strftime') else str(created_at)}
<b>Статус:</b> {status}

<b>Товары:</b>
{''.join(items_text)}

<b>Адрес доставки:</b>
{order.get('shipping_address', 'Не указан')}

<b>Способ оплаты:</b>
{get_payment_method_description(order.get('payment_method', ''))}

<b>Итого:</b> {total} ₽
"""
    return result

def get_order_status_emoji(status):
    """Возвращает эмодзи для статуса заказа"""
    statuses = {
        'new': '🆕',
        'processing': '⏳',
        'shipped': '🚚',
        'delivered': '✅',
        'canceled': '❌'
    }
    return statuses.get(status, '❓')

def get_status_description(status):
    """Возвращает описание статуса заказа"""
    statuses = {
        'new': 'Новый',
        'processing': 'В обработке',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен',
        'canceled': 'Отменен'
    }
    return statuses.get(status, 'Неизвестно')

def get_payment_method_description(method):
    """Возвращает описание способа оплаты"""
    methods = {
        'card': '💳 Оплата картой',
        'cash': '💵 Оплата наличными при получении'
    }
    return methods.get(method, 'Не указан') 