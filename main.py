import os
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from flask import Flask
from threading import Thread
from trainings import trainings

# Конфигурация
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
START_DATE = datetime(2025, 6, 30)

# Flask-приложение для Render
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Samuel CrossFit Bot is running."

@web_app.route("/ping")
def ping():
    return "pong"

# Ответы на кнопку "Выполнено"
REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

# Отправка ежедневной тренировки
async def send_training():
    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 0:  # 09:00 по МСК
            delta_days = (now.date() - START_DATE.date()).days
            day_index = delta_days % len(trainings)
            training = trainings[day_index]
            text = f"🏋️ День {day_index + 1}: {training['title']}\n\n{training['description']}\n\n✅ Выполнено?"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выполнено ✅", callback_data="done")]
            ])
            if CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard)
        await asyncio.sleep(60)

# Реакция на кнопку "Выполнено"
@dp.callback_query()
async def on_button(callback: types.CallbackQuery):
    if callback.data == "done":
        reply = random.choice(REACTIONS)
        await callback.answer(reply, show_alert=True)

# Ответ на любое текстовое сообщение
@dp.message()
async def on_message(message: types.Message):
    await message.reply("✅ Бот работает и ждёт следующую тренировку!")

# Асинхронный запуск бота
async def main():
    asyncio.create_task(send_training())
    await dp.start_polling(bot)

# Запуск Flask-сервера
def run_flask():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Основной блок
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(main())
