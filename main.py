# main.py
# Telegram-бот с ежедневной рассылкой тренировок для деплоя на Render.

import os
import asyncio
import threading
import random
from datetime import datetime, time, timedelta

from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from trainings import trainings

# Конфигурация бота
API_TOKEN = "8129538051:AAFf27Hn0cWvTLDjbnTEtY9sTvpx_VIjRyU"
CHAT_ID = 246801537

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список мотивационных фраз для ответа на нажатие кнопки
motivational_phrases = [
    "Отличная работа! Продолжай в том же духе.",
    "Так держать! 💪",
    "Молодец! Еще один шаг к цели.",
    "Вперед к новым достижениям!",
    "Ты справился, гордимся тобой! ✅"
]

# Обработчик нажатия кнопки "Выполнено ✅"
@dp.callback_query(F.data == "done")
async def on_done_button(callback: CallbackQuery):
    # Подтверждаем нажатие, чтобы убрать "часики" у кнопки
    await callback.answer()
    # Отправляем случайную мотивационную фразу в ответ
    phrase = random.choice(motivational_phrases)
    await callback.message.reply(phrase)

# Функция отправки ежедневного сообщения с тренировкой
async def send_daily_message():
    # Рассчитываем паузу до следующего 6:30 UTC (9:30 по Москве)
    now = datetime.utcnow()
    target_time = datetime.combine(now.date(), time(6, 30))
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    # Ожидаем до запланированного времени
    await asyncio.sleep(wait_seconds)
    # После ожидания – цикл ежедневной отправки сообщений
    while True:
        # Берем очередную тренировку из списка
        training = trainings[send_daily_message.current_index]
        title = training["title"]
        desc = training["description"]
        text = f"{title}\\n\\n{desc}"
        # Кнопка "Выполнено ✅" под сообщением
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Выполнено ✅", callback_data="done")]
        ])
        # Отправляем сообщение с тренировкой
        await bot.send_message(CHAT_ID, text, reply_markup=keyboard)
        # Переходим к следующей тренировке (циклично по списку)
        send_daily_message.current_index = (send_daily_message.current_index + 1) % len(trainings)
        # Ждем 24 часа до следующего дня
        await asyncio.sleep(24 * 60 * 60)

# Инициализируем индекс для цикличного перебора тренировок
send_daily_message.current_index = 0

# Основная асинхронная функция запуска бота
async def main():
    # Запускаем задачу ежедневной отправки сообщений
    asyncio.create_task(send_daily_message())
    # Запускаем бота (долгополлинг Telegram)
    await dp.start_polling(bot, skip_updates=True)

# Функция для запуска бота в отдельном потоке
def start_bot():
    asyncio.run(main())

# Инициализация Flask-приложения (для Render)
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running"

# Запуск Flask-сервера и фонового потока бота
if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
