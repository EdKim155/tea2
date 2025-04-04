import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

# Категории чая
TEA_CATEGORIES = {
    'black': 'Черный чай 🖤',
    'green': 'Зеленый чай 💚',
    'white': 'Белый чай 🤍',
    'oolong': 'Улун 🧡',
    'herbal': 'Травяной чай 💜',
    'fruit': 'Фруктовый чай 🍓'
}

# Ассортимент чая
TEA_PRODUCTS = {
    'black': [
        {'id': 'b1', 'name': 'Ассам', 'description': 'Крепкий черный чай из Индии с солодовым вкусом', 'price': 350, 'image': 'assam.jpg'},
        {'id': 'b2', 'name': 'Эрл Грей', 'description': 'Черный чай с ароматом бергамота', 'price': 380, 'image': 'earl_grey.jpg'},
        {'id': 'b3', 'name': 'Дарджилинг', 'description': 'Изысканный черный чай с мускатным оттенком', 'price': 450, 'image': 'darjeeling.jpg'},
    ],
    'green': [
        {'id': 'g1', 'name': 'Сенча', 'description': 'Традиционный японский зеленый чай', 'price': 400, 'image': 'sencha.jpg'},
        {'id': 'g2', 'name': 'Жасминовый', 'description': 'Зеленый чай с нежным ароматом жасмина', 'price': 370, 'image': 'jasmine.jpg'},
        {'id': 'g3', 'name': 'Ганпаудер', 'description': 'Китайский зеленый чай с дымным ароматом', 'price': 320, 'image': 'gunpowder.jpg'},
    ],
    'white': [
        {'id': 'w1', 'name': 'Бай Му Дань', 'description': 'Белый пионовый чай с нежным вкусом', 'price': 520, 'image': 'bai_mu_dan.jpg'},
        {'id': 'w2', 'name': 'Серебряные иглы', 'description': 'Элитный белый чай из типсов', 'price': 680, 'image': 'silver_needle.jpg'},
    ],
    'oolong': [
        {'id': 'o1', 'name': 'Те Гуань Инь', 'description': 'Слабоферментированный улун с цветочными нотами', 'price': 550, 'image': 'tie_guan_yin.jpg'},
        {'id': 'o2', 'name': 'Да Хун Пао', 'description': 'Темный улун с насыщенным вкусом', 'price': 620, 'image': 'da_hong_pao.jpg'},
    ],
    'herbal': [
        {'id': 'h1', 'name': 'Ромашковый', 'description': 'Успокаивающий травяной чай', 'price': 280, 'image': 'chamomile.jpg'},
        {'id': 'h2', 'name': 'Мятный', 'description': 'Освежающий чай с мятой перечной', 'price': 260, 'image': 'mint.jpg'},
    ],
    'fruit': [
        {'id': 'f1', 'name': 'Ягодный микс', 'description': 'Фруктовый чай с малиной, клубникой и черникой', 'price': 340, 'image': 'berry_mix.jpg'},
        {'id': 'f2', 'name': 'Цитрусовый', 'description': 'Фруктовый чай с апельсином и лимоном', 'price': 320, 'image': 'citrus.jpg'},
    ],
}

# Оформление сообщений
WELCOME_MESSAGE = """
<b>🍵 Добро пожаловать в TeaShopBot! 🍵</b>

Здесь вы найдете лучшие сорта чая со всего мира.
Наслаждайтесь приятным шоппингом!
"""

ABOUT_MESSAGE = """
<b>О нашем магазине</b>

Мы предлагаем эксклюзивную коллекцию чаев высочайшего качества, собранных со всего мира.

<b>Наши преимущества:</b>
✅ Тщательный отбор поставщиков
✅ Свежеобжаренные чаи
✅ Бережная упаковка
✅ Быстрая доставка

<b>Контакты:</b>
📱 Телефон: +7-XXX-XXX-XXXX
📧 Почта: info@teashop.ru
🌐 Сайт: teashop.ru
"""

REGISTER_MESSAGE = """
<b>Регистрация в TeaShopBot</b>

Для завершения регистрации, пожалуйста, поделитесь своим номером телефона, нажав на кнопку ниже.

Ваши данные будут использоваться только для обработки заказов и не будут переданы третьим лицам.
""" 