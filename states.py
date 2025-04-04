from telegram.ext import ConversationHandler

# Основные состояния
MAIN_MENU = 0
VIEWING_CATEGORIES = 1
VIEWING_PRODUCTS = 2
VIEWING_PRODUCT_DETAILS = 3
VIEWING_CART = 4
CHECKOUT = 5
AWAITING_ADDRESS = 6
AWAITING_CONFIRMATION = 7
REGISTRATION = 8
VIEWING_PROFILE = 9
VIEWING_ORDERS = 10
VIEWING_ORDER_DETAILS = 11
CONTACT_US = 12

# Словарь для хранения временных данных пользователей
user_data = {}

# Данные для хранения контекста просмотра категорий/товаров
class UserContext:
    def __init__(self):
        self.current_category = None  # Текущая категория
        self.current_product = None   # Текущий просматриваемый товар
        self.checkout_data = {}       # Данные для оформления заказа

    def set_category(self, category_key):
        """Устанавливает текущую категорию"""
        self.current_category = category_key
        self.current_product = None
        
    def set_product(self, product_id):
        """Устанавливает текущий товар"""
        self.current_product = product_id
        
    def set_checkout_data(self, key, value):
        """Сохраняет данные для оформления заказа"""
        self.checkout_data[key] = value
        
    def get_checkout_data(self):
        """Возвращает данные для оформления заказа"""
        return self.checkout_data
        
    def clear_checkout_data(self):
        """Очищает данные для оформления заказа"""
        self.checkout_data = {}

def get_user_context(user_id):
    """Получает контекст пользователя или создает новый"""
    if user_id not in user_data:
        user_data[user_id] = UserContext()
    return user_data[user_id] 