import os
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# Кастомные реакции на кнопку
REACTIONS = [
    "Отлично, продолжаем в том же духе! 💪",
    "Тренировка засчитана! До завтра 🏋️",
    "Красавчик! Один шаг ближе к цели 🔥",
    "Так держать! Увидимся на следующей тренировке 👊",
    "Молодец! Главное — стабильность 🙌"
]

async def send_training():
    sent_today = False
    while True:
        now = datetime.utcnow()

        # 09:00 МСК = 06:00 UTC
        if now.hour == 6 and now.minute in (0, 1, 2) and not sent_today:
            delta_days = (now.date() - START_DATE.date()).days
            day_index = delta_days % len(trainings)
            training = trainings[day_index]

            text = f"🏋️ День {day_index + 1}: {training['title']}\n\n{training['description']}\n\n✅ Выполнено?"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Выполнено ✅", callback_data="done")]
                ]
            )

            if CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard)
                sent_today = True

        if now.hour == 0 and now.minute == 0:
            sent_today = False

        await asyncio.sleep(60)

@dp.message(F.text.lower() == "/ping")
async def ping_reply(message: types.Message):
    await message.answer("✅ Бот работает. Готов к следующей тренировке!")

@dp.callback_query()
async def on_button_press(callback: types.CallbackQuery):
    if callback.data == "done":
        reply = random.choice(REACTIONS)
        await callback.answer(reply, show_alert=True)

@dp.startup()
async def on_startup(dispatcher):
    asyncio.create_task(send_training())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
