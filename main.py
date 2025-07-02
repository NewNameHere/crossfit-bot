import os
import logging
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher
from trainings import trainings
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)
dp = Dispatcher()
START_DATE = datetime(2025, 6, 30)

# Flask app to keep Render happy
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Samuel CrossFit Bot is running."

@web_app.route("/ping")
def ping():
    return "pong"

async def send_training():
    while True:
        now = datetime.utcnow()
        if now.hour == 10 and now.minute == 0:
            delta_days = (now.date() - START_DATE.date()).days
            day_index = delta_days % 28
            training = trainings[day_index]
            text = f"🏋️ День {day_index + 1}: {workout['title']}\n\n{workout['description']}"

{training}

text = f"🏋️ День {day_index + 1}:\n{training}\n\n✅ Выполнено?"

            if CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=text)
        await asyncio.sleep(60)

@dp.startup()
async def on_startup(dispatcher):
    asyncio.create_task(send_training())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
