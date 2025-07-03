import os
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from flask import Flask
from trainings import trainings

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
START_DATE = datetime(2025, 6, 30)

# Flask app to keep Render alive
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Samuel CrossFit Bot is running."

@web_app.route("/ping")
def ping():
    return "pong"

# Список кастомных реакций
REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

# Рассылка тренировки
async def send_training():
    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 0:  # 09:00 МСК
            delta_days = (now.date() - START_DATE.date()).days
            day_index = delta_days % len(trainings)
            training = trainings[day]()
