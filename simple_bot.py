import logging
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- База данных ---
conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    city TEXT NOT NULL,
    shop TEXT,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    is_custom BOOLEAN DEFAULT 0,  
    size TEXT,
    model TEXT,
    color TEXT,
    created_at TEXT
)
''')
conn.commit()

# --- Состояния ---
class RequestForm(StatesGroup):
    city = State()
    shop = State()
    category = State()
    brand = State()
    custom_brand = State()
    model = State()
    size = State()
    color = State()

# --- Клавиатуры ---
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("🚀 Нет товара"))

cities = {
    "Абакан", "Архангельск", "Брянск", "Екатеринбург", "Геленджик", "Иркутск", "Ижевск",
    "Калуга", "Казань", "Киров", "Краснодар", "Красноярск", "Липецк", 
    "Москва и область", "Нижний Новгород и область", "Новокузнецк", "Новороссийск", "Новосибирск", "Обнинск", "Омск",
    "Пермь", "Ростов-на-Дону", "Санкт-Петербург и область", "Саратов", "Сочи", "Сургут",
    "Сыктывкар", "Тула", "Тюмень", "Владимир", "Волгоград", "Воронеж", "Ярославль",
    "Южно-Сахалинск"
}

city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
city_keyboard.add(*[KeyboardButton(city) for city in sorted(cities)])

city_shops = {
    "Архангельск":["Макси", "Титан Арена"],
"Москва и область": [
    "Авиапарк",
    "Акварель",
    "Атриум",
    "Афимолл",
    "Белая дача",
    "Белая дача Urban",
    "Европолис",
    "Fashion House",
    "Измайловский Пассаж",
    "Каширская Плаза",
    "Колумбус",
    "Красная Пресня",
    "Красный Кит",
    "Кузнецкий мост",
    "Метрополис",
    "Новая Рига",
    "Орджоникидзе",
    "Охотный ряд",
    "Павелецкая Плаза",
    "РИО",
    "Саларис",
    "Савеловский",
    "Сокольники",
    "Vegas Каширское",
    "Vegas Кунцево",
    "Vegas Сити",
    "XL"
],
    "Сургут": [
        "Аура",
        "Росич"
    ],
    "Санкт-Петербург и область": [
           "Академический",
    "Fashion House",
    "Галерея",
    "Лето",
    "Охта Молл",
    "Румба",
    "Южный Полюс"
    ],
    "Екатеринбург": [
        "Гринвич", "Омега","Brands Stories outlet"
    ],
    "Иркутск":["Модный Квартал", "Юбилейный"],
    "Краснодар": [
        "Галерея Краснодар", "ОЗ Молл", "Меридиан",
    ],
    "Нижний Новгород и область":["Небо","Мега"],
    "Новосибирск":["Аура", "Континент"]
    
}


shop_keyboards = {
    city: ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(*[KeyboardButton(shop) for shop in sorted(shops)])
    for city, shops in city_shops.items()
}

categories = ["одежда", "обувь", "аксуссуары", "другая"]

category_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
category_keyboard.add(*[KeyboardButton(category) for category in categories])


colors = [
    "черный", "белый", "серый", "бежевый", "желтый",
    "зеленый", "голубой", "коричневый", "красный",
    "мультиколор", "оранжевый", "прозрачный", "розовый",
    "синий", "фиолетовый", "другой"
]

color_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
color_keyboard.add(*[KeyboardButton(color) for color in colors])

brands = [
    "adidas",
    "adidas Originals",
     "Nike",
     "PUMA",
    "Reebok",
     "Under Armour",
    "New Balance",
      "Peak",
     "Hike",
    "adidas YEEZY",
    "Alo Yoga",
    "Alpha Industries",
    "ASICS",
    "Bona Fide",
    "Boss",
    "Buff",
    "Calvin Klein Performance",
    "Calvin Klein Underwear",
    "Carhartt WIP",
    "Champion",
    "Colmar",
    "Cream Yoga",
    "Deha",
    "Diesel",
    "EA7",
    "Ecco",
    "Etudes",
    "Euphoria",
    "Golden Goose",
    "Gri",
    "GTS",
    "Haikure",
    "Heroine Sport",
    "Hike",
    "Hoka One One",
    "Hugo",
    "Icepeak",
    "Jogel",
    "Jordan",
    "Kerry",
    "Krakatau",
    "Lacoste",
    "Lassie",
    "Li-Ning",
    "LumberJack",
    "Luhta",
    "Mademan",
    "Mark Formelle",
    "Mela",
    "Mizuno",
    "Nativos",
    "New Balance",
    "Nike",
    "Nike ACG",
    "Nux",
    "Obey",
    "Oakley",
    "On",
    "Peak",
    "Premiata",
    "PUMA",
    "Reebok",
    "Reima",
    "Salomon",
    "Saucony",
    "Skandiwear",
    "Solemate",
    "Speedo",
    "Sporty & Rich",
    "Stone Island",
    "The North Face",
    "The Ragged Priest",
    "TheJoggConcept",
    "Ternua",
    "Tyr",
    "UGG",
    "Uglow",
    "Under Armour",
    "Vans",
    "Veja",
    "Viking",
    "Vtr",
    "Wilson",
    "Xtep",
    "ZNY"
]

main_brands = [
    "adidas", "adidas Originals", "Nike",  "Reebok",  "PUMA",  "Under Armour",  "New Balance", "Peak", "Hike", "Mademan", 
      "Champion", "On", "Sporty & Rich", "Cream Yoga", "Lacoste"
     
]
other_brands = [b for b in brands if b not in main_brands]

main_brands_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
for brand in main_brands:
    main_brands_keyboard.insert(KeyboardButton(brand))
main_brands_keyboard.add(KeyboardButton("✏️ Ввести другой бренд"))



# --- Хендлеры ---

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Нажми кнопку Нет товара, чтобы начать:", reply_markup=start_keyboard)

@dp.message_handler(Text(equals="🚀 Нет товара"), state="*")
async def start_survey(message: types.Message, state: FSMContext):
    await message.answer("Выбери город:", reply_markup=city_keyboard)
    await RequestForm.city.set()


@dp.message_handler(state=RequestForm.city)
async def process_city(message: types.Message, state: FSMContext):
    if message.text not in cities:
        await message.reply("Пожалуйста, выбери город из предложенного списка.")
        return
    
    await state.update_data(city=message.text)
    
    if message.text in city_shops:
        await message.answer(f"Выбери магазин в {message.text}:", 
                           reply_markup=shop_keyboards[message.text])
        await RequestForm.shop.set()
    else:
        await message.answer("Выбери категорию:", reply_markup=main_brands_keyboard)
        await RequestForm.category.set()

@dp.message_handler(state=RequestForm.shop)
async def process_shop(message: types.Message, state: FSMContext):
    data = await state.get_data()
    city = data['city']
    
    if city not in city_shops or message.text not in city_shops[city]:
        await message.reply(f"Пожалуйста, выбери магазин из списка для {city}.", 
                          reply_markup=shop_keyboards[city])
        return
    
    await state.update_data(shop=message.text)
    await message.answer(f"Выбери категорию:", reply_markup=main_brands_keyboard)
    await RequestForm.category.set()
    
@dp.message_handler(state=RequestForm.category)
async def process_category(message: types.Message, state: FSMContext):
    if message.text not in categories:
        await message.reply("Пожалуйста, выбери категорию из предложенного списка.")
        return
        await message.answer("Выбери бренд:", reply_markup=main_brands_keyboard)
        await RequestForm.brand.set()

@dp.message_handler(state=RequestForm.brand)
async def process_brand(message: types.Message, state: FSMContext):
    if message.text == "✏️ Ввести другой бренд":
        await message.answer("Выбери бренд:", reply_markup=ReplyKeyboardRemove())
        await RequestForm.custom_brand.set()  # Переходим в состояние для кастомного бренда
        return
    
    if message.text in main_brands:
        await state.update_data(brand=message.text, is_custom=0)
        await message.answer(f"Введи модель", reply_markup=ReplyKeyboardRemove())
        await RequestForm.model.set() 
    else:
        await message.answer("Пожалуйста, выбери бренд из списка или нажми 'Ввести другой бренд'", 
                          reply_markup=brands_keyboard)

@dp.message_handler(state=RequestForm.custom_brand)
async def process_custom_brand(message: types.Message, state: FSMContext):
    custom_brand = message.text.strip()
    
    if len(custom_brand) < 2:
        await message.answer("Название бренда должно содержать минимум 2 символа. Попробуйте еще раз:")
        return
    
    await state.update_data(brand=custom_brand, is_custom=1)
    await message.answer(f"Введи модель:", reply_markup=ReplyKeyboardRemove())
    await RequestForm.model.set()

@dp.message_handler(state=RequestForm.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.reply("Введи размер:")
    await RequestForm.size.set()

@dp.message_handler(state=RequestForm.size)
async def process_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.reply("Выбери цвет:", reply_markup=color_keyboard)
    await RequestForm.color.set()

@dp.message_handler(state=RequestForm.color)
async def process_color(message: types.Message, state: FSMContext):
    if message.text not in colors:
        await message.reply("Пожалуйста, выбери цвет из предложенного списка.")
        return
    
    await state.update_data(color=message.text)
    data = await state.get_data()

    # --- Сохраняем в БД
    cursor.execute('''
       INSERT INTO requests 
    (user_id, city, shop, brand, is_custom, size, model, color, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.from_user.id,
        data['city'],
        data.get('shop'),
        data.get('category'),
        data['brand'],
        data.get('is_custom', 0),
        data.get('size'),
        data.get('model'),
        data.get('color'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    
    await message.answer("Спасибо! Данные сохранены! Чтобы внести ещё одну — снова нажми 🚀 Нет товара.", reply_markup=start_keyboard)
    await state.finish()

# --- Фильтр случайных сообщений до начала ---
@dp.message_handler(state="*")
async def block_unexpected(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Пожалуйста, нажми кнопку 🚀 Нет товара.", reply_markup=start_keyboard)

# --- Запуск ---
if __name__ == '__main__':
    print("Бот запущен")
    executor.start_polling(dp, skip_updates=True)
