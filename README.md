# Samuel CrossFit Bot (Web Service)

Бот для Telegram, который отправляет тренировку каждый день в 10:00 UTC.

## 🔧 Настройка на Render (БЕСПЛАТНО)

1. Создай репозиторий на GitHub и загрузи туда все файлы из этого архива.
2. Перейди на https://render.com и нажми "New +" → **Web Service**
3. Выбери репозиторий и подтверди.
4. Добавь переменные окружения:
   - TELEGRAM_BOT_TOKEN — токен из @BotFather
   - CHAT_ID — твой chat_id из @userinfobot
5. Убедись, что Render распознал `render.yaml`, и нажми **Manual Deploy**.

Бот запустится в фоне и будет слать тренировку каждый день.
