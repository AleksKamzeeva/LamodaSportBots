import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3
import csv
from datetime import datetime, timedelta
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

DB_PATH = "requests.db"

# --- Клавиатуры ---
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("Выгрузить файлы"))

# --- Хендлер запуска /start ---
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Нажми кнопку ниже, чтобы выгрузить файлы:", reply_markup=start_keyboard)

# --- Функция выгрузки CSV ---
def export_to_csv(query, filename):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    conn.close()

    with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)

# --- Хендлер по кнопке "Выгрузить файлы" ---
@dp.message_handler(Text(equals="Выгрузить файлы"), state="*")
async def send_exports(message: types.Message, state: FSMContext):
    yesterday = (datetime.now() - timedelta(days=1)).date()
    query_yesterday = f"""
        SELECT * FROM requests
        WHERE DATE(created_at) = '{yesterday}'
    """
    export_to_csv(query_yesterday, "requests_yesterday.csv")

    query_all = "SELECT * FROM requests"
    export_to_csv(query_all, "requests_all.csv")

    await message.answer("Отправляю выгрузки:")
    await message.answer_document(types.InputFile("requests_yesterday.csv"))
    await message.answer_document(types.InputFile("requests_all.csv"))

    os.remove("requests_yesterday.csv")
    os.remove("requests_all.csv")

if __name__ == "__main__":
    print("Бот запущен!")
    executor.start_polling(dp, skip_updates=True)
