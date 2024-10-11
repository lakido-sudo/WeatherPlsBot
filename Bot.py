import os
import requests
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from Models import Log, SessionLocal, UserSettings
import time

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена бота и ключа API погоды из переменных окружения
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, timeout=10)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """
    Обработчик команды /start.

    Отправляет приветственное сообщение пользователю и инструкции по использованию бота.

    Args:
        message (types.Message): Сообщение от пользователя.
    """
    logger.info(f"Received /start command from {message.from_user.full_name}")
    await message.answer(
        "Привет! Я бот для получения информации о погоде.\n"
        "Используйте команду /weather <город>, чтобы узнать погоду.\n"
        "Установите предпочитаемый город /set_city <город>."
    )


# Кэш для хранения данных о погоде
weather_cache = {}

cache_expiration_time = 300  # Время жизни кэша в секундах (например, 5 минут)


@dp.message(Command("weather"))
async def send_weather(message: types.Message):
    """
    Обработчик команды /weather.

    Получает текущую погоду в указанном городе и отправляет информацию пользователю.

    Args:
        message (types.Message): Сообщение от пользователя, содержащее команду и город.

    Raises:
        IndexError: Если город не указан в команде.
    """

    # Извлечение названия города из сообщения
    city = message.text[len("/weather "):].strip()  # Убираем "/weather " и пробелы по краям

    if not city:
        # Если город не указан, проверяем настройки пользователя
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == message.from_user.id).first()

        if settings and settings.preferred_city:
            city = settings.preferred_city
            logger.info(f"No city provided, using preferred city: {city}")
        else:
            await message.answer(
                "Пожалуйста, укажите город после команды /weather или установите его после команды /set_city.")
            return

    logger.info(f"Received weather request for city: {city} from {message.from_user.full_name}")

    # Проверка наличия данных в кэше и их актуальности
    current_time = time.time()
    if city in weather_cache and (current_time - weather_cache[city]['timestamp'] < cache_expiration_time):
        logger.info(f"Returning cached data for city: {city}")
        weather_data = weather_cache[city]['data']
    else:
        # Запрос к API погоды для получения данных о погоде в указанном городе
        response = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
        )

        # Логирование ответа от API погоды
        logger.info(f"Response from weather API: {response.status_code}, {response.text}")

        if response.status_code == 200:
            weather_data = response.json()  # Преобразование ответа в формат JSON

            # Кэшируем данные о погоде
            weather_cache[city] = {
                'data': weather_data,
                'timestamp': current_time
            }
        else:
            logger.error(f"Error fetching weather data for city: {city}, status code: {response.status_code}")
            await message.answer("Ошибка: Город не найден или указан неверно.")
            return

    # Формирование сообщения с данными о погоде
    message_text = (f"Погода в {weather_data['name']}:\n"
                    f"Температура: {weather_data['main']['temp']}°C\n"
                    f"Ощущается как: {weather_data['main']['feels_like']}°C\n"
                    f"Описание: {weather_data['weather'][0]['description']}\n"
                    f"Влажность: {weather_data['main']['humidity']}%\n"
                    f"Скорость ветра: {weather_data['wind']['speed']} м/с")

    await message.answer(message_text)  # Отправка информации о погоде пользователю

    # Логируем запрос в базу данных
    db: Session = SessionLocal()  # Создание сессии для работы с базой данных
    log_entry = Log(user_id=message.from_user.id, command=message.text, response=message_text)
    db.add(log_entry)  # Добавление записи в базу данных
    db.commit()  # Сохранение изменений в базе данных
    db.close()  # Закрытие сессии


@dp.message(Command("set_city"))
async def set_city(message: types.Message):
    """Устанавливает предпочитаемый город для пользователя."""
    try:
        # Извлечение названия города из сообщения
        city = message.text[len("/set_city "):].strip()  # Убираем "/set_city " и пробелы по краям
        db: Session = SessionLocal()

        if not city:
            # Если город не указан, отправляем сообщение с просьбой указать его
            await message.answer("Пожалуйста, укажите город после команды /set_city. Пример: /set_city Москва.")
            return

        # Сохраняем или обновляем настройки пользователя
        settings = db.query(UserSettings).filter(UserSettings.user_id == message.from_user.id).first()
        if settings:
            settings.preferred_city = city  # Обновляем существующий город
        else:
            settings = UserSettings(user_id=message.from_user.id, preferred_city=city)  # Создаем новую запись
            db.add(settings)

        db.commit()  # Сохраняем изменения в базе данных
        db.close()  # Закрываем сессию

        await message.answer(f"Предпочитаемый город установлен на: {city}")  # Подтверждение пользователю
    except Exception as e:
        logger.error(f"Error setting preferred city: {e}")
        await message.answer("Произошла ошибка при установке предпочитаемого города.")

@dp.message(Command("get_city"))
async def get_city(message: types.Message):
    """Получает предпочитаемый город для пользователя."""
    db: Session = SessionLocal()
    settings = db.query(UserSettings).filter(UserSettings.user_id == message.from_user.id).first()

    if settings:
        await message.answer(f"Ваш предпочитаемый город: {settings.preferred_city}")
    else:
        await message.answer("Предпочитаемый город не установлен.")

    db.close()

if __name__ == "__main__":
    import asyncio


    async def main():
        """
        Основная функция для запуска бота.

        Запускает процесс опроса обновлений от Telegram.
        """
        await dp.start_polling(bot)  # Передаем экземпляр бота в метод


    asyncio.run(main())  # Запуск основной функции
