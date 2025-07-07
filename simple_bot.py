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
BOT_TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- База данных ---
conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    city TEXT NOT NULL,
    brand TEXT NOT NULL,
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
    brand = State()
    size = State()
    model = State()
    color = State()

# --- Клавиатуры ---
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("🚀 Нет товара"))

cities = [
    "Абакан", "Архангельск", "Брянск", "Екатеринбург", "Геленджик", "Иркутск", "Ижевск",
    "Калуга", "Казань", "Киров", "Краснодар", "Красноярск", "Липецк", "Москва",
    "Нижний Новгород", "Новокузнецк", "Новороссийск", "Новосибирск", "Обнинск", "Омск",
    "Пермь", "Ростов-на-Дону", "Санкт-Петербург", "Саратов", "Сочи", "Сургут",
    "Сыктывкар", "Тула", "Тюмень", "Владимир", "Волгоград", "Воронеж", "Ярославль",
    "Южно-Сахалинск"
]

city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
city_keyboard.add(*[KeyboardButton(city) for city in cities])

# --- Хендлеры ---

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Нажми кнопку ниже, чтобы начать:", reply_markup=start_keyboard)

@dp.message_handler(Text(equals="🚀 Нет товара"), state="*")
async def start_survey(message: types.Message, state: FSMContext):
    await message.answer("Выбери город:", reply_markup=city_keyboard)
    await RequestForm.city.set()

@dp.message_handler(state=RequestForm.city)
async def process_city(message: types.Message, state: FSMContext):
    print(f"[DEBUG] Получен город: {message.text}")
    if message.text not in cities:
        await message.reply("Пожалуйста, выбери город из предложенного списка.")
        return
    await state.update_data(city=message.text)
    await message.reply("Теперь введи бренд:", reply_markup=ReplyKeyboardRemove())
    await RequestForm.brand.set()

@dp.message_handler(state=RequestForm.brand)
async def process_brand(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.reply("Введи размер (можно пропустить):")
    await RequestForm.size.set()

@dp.message_handler(state=RequestForm.size)
async def process_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.reply("Введи модель (можно пропустить):")
    await RequestForm.model.set()

@dp.message_handler(state=RequestForm.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.reply("Введи цвет (можно пропустить):")
    await RequestForm.color.set()

@dp.message_handler(state=RequestForm.color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    data = await state.get_data()

    # Сохраняем в БД
    cursor.execute('''
        INSERT INTO requests (user_id, city, brand, size, model, color, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.from_user.id,
        data['city'],
        data['brand'],
        data.get('size'),
        data.get('model'),
        data.get('color'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

    await message.reply("Спасибо! Запись сохранена. Чтобы внести ещё одну — снова нажми 🚀 Нет товара.", reply_markup=start_keyboard)
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
