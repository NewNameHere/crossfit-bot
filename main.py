import os
import logging
import asyncio
import random
from datetime import datetime
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from trainings import trainings

# Получаем переменные окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Настройка бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
START_DATE = datetime(2025, 6, 30)

# Flask-приложение для Render (не даст уснуть боту)
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Samuel CrossFit Bot is running."

@web_app.route("/ping")
def ping():
    return "pong"

# Ответы на кнопку
REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

# Отправка тренировок в 09:00 по Москве (06:00 UTC)
async def send_training():
    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 0:
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

# Ответ на кнопку
@dp.callback_query()
async def on_button_press(callback: types.CallbackQuery):
    if callback.data == "done":
        reply = random.choice(REACTIONS)
        await callback.answer(reply, show_alert=True)

# Ответ на любое текстовое сообщение — чтобы проверить, что бот работает
@dp.message()
async def on_message(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="✅ Бот работает и ждёт следующую тренировку!")

# Запуск бота
@dp.startup()
async def on_startup(dispatcher):
    asyncio.create_task(send_training())

# Точка входа
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
