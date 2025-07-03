import os
import logging
import asyncio
import random
from datetime import datetime
from flask import Flask
from threading import Thread

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from trainings import trainings

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

app = Flask(__name__)

@app.route("/")
def home():
    return "Samuel CrossFit Bot is running."

START_DATE = datetime(2025, 6, 30)

REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

async def send_daily_workout():
    while True:
        now = datetime.utcnow()
        if now.hour == 6 and now.minute == 0:
            delta_days = (now.date() - START_DATE.date()).days
            index = delta_days % len(trainings)
            training = trainings[index]

            text = f"🏋️ День {index + 1}: {training['title']}\n\n{training['description']}\n\n✅ Выполнено?"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выполнено ✅", callback_data="done")]
            ])
            if CHAT_ID:
                await bot.send_message(CHAT_ID, text, reply_markup=keyboard)

        await asyncio.sleep(60)

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    if call.data == "done":
        await call.answer(random.choice(REACTIONS), show_alert=True)

@dp.message()
async def handle_any_message(message: types.Message):
    await message.answer("✅ Бот работает! Напоминания придут автоматически.")

async def start_bot():
    await dp.start_polling(bot)

def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(send_daily_workout())
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Thread(target=run_asyncio_loop).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
