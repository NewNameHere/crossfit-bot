import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
import threading
import random
from datetime import datetime, time, timedelta
from trainings import trainings

API_TOKEN = "8129538051:AAFf27Hn0cWvTLDjbnTEtY9sTvpx_VIjRyU"
CHAT_ID = 246801537
SEND_HOUR = 9
SEND_MINUTE = 30

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
app = Flask(__name__)

def get_random_training():
    return random.choice(trainings)

def get_training_message(training):
    return f"<b>{training['title']}</b>\n{training['description']}"

@dp.message(F.text)
async def handle_user_message(message: types.Message):
    await message.answer("Бот работает ✅\nОжидайте тренировку утром в 9:30 по МСК.")

@dp.callback_query(F.data == "done")
async def done_callback(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Отлично! Продолжаем в том же духе 💪")

async def send_daily_training():
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(SEND_HOUR, SEND_MINUTE))
        if now >= target_time:
            target_time += timedelta(days=1)
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        training = get_random_training()
        message = get_training_message(training)

        builder = InlineKeyboardBuilder()
        builder.button(text="Выполнено ✅", callback_data="done")
        await bot.send_message(chat_id=CHAT_ID, text=message, reply_markup=builder.as_markup())

@app.route("/")
def index():
    return "Bot is running!"

def start_flask():
    app.run(host="0.0.0.0", port=10000)

async def main():
    threading.Thread(target=start_flask).start()
    asyncio.create_task(send_daily_training())
    await dp.start_polling(bot, handle_signals=False)

if __name__ == "__main__":
    asyncio.run(main())