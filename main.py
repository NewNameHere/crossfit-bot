import os
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from trainings import trainings

# Получаем переменные окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
START_DATE = datetime(2025, 6, 30)

# Инициализация Telegram-бота и Flask-сервера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
web_app = Flask(__name__)

# Фразы при нажатии на кнопку
REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

# Главная страница Flask
@web_app.route("/")
def home():
    return "Samuel CrossFit Bot is running."

@web_app.route("/ping")
def ping():
    return "pong"

# Задача: ежедневная рассылка тренировок
async def send_training():
    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 0:  # 09:00 по Москве (UTC+3)
            delta_days = (now.date() - START_DATE.date()).days
            day_index = delta_days % len(trainings)
            training = trainings[day_index]

            text = f"🏋️ День {day_index + 1}: {training['title']}\n\n{training['description']}\n\n✅ Выполнено?"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Выполнено ✅", callback_data="done")]]
            )

            if CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard)

        await asyncio.sleep(60)

# Обработка кнопки ✅
@dp.callback_query()
async def on_button_press(callback: types.CallbackQuery):
    if callback.data == "done":
        reply = random.choice(REACTIONS)
        await callback.answer(reply, show_alert=True)

# Команда /ping для проверки работы
@dp.message()
async def handle_ping(msg: types.Message):
    if msg.text.lower() == "/ping":
        await msg.answer("Бот работает ✅")

# Запуск всех задач
async def main():
    asyncio.create_task(send_training())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
