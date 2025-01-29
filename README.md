# WeatherPlsBot

## Описание
**WeatherPlsBot** — это Telegram-бот, который предоставляет пользователю информацию о погоде и хранит данные о пользователе и его запросах.

![WeatherPlsBot](https://i.ibb.co/zVBRXYJc/2025-01-29-13-56-33.png)

## Установка и запуск

### Необходимые действия
1. **Настройка окружения**:
   - В файле `.env` необходимо указать токен бота и токен сервиса погоды.
   
2. **Установка зависимостей**:
   - Список зависимостей находится в файле `requirements.txt`.
   - Установите зависимости в виртуальном окружении:
     ```
     # Перейдите в каталог проекта
     cd /path/to/your/project
     
     # Активируйте виртуальное окружение
     # Для Mac/Linux:
     source .venv/bin/activate

     # Для Windows:
     .\.venv\Scripts\activate
     ```
   - Установите зависимости из файла `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```

3. **Локальный запуск**:
   - Запустите API:
     ```
     uvicorn Api:app --reload
     ```
   - Запустите бота (Вы также можете нажать кнопку "Play" в вашем редакторе.):
     ```
     python Bot.py
     ```
   - Перейдите в бота и нажмите (или введите):
     ```
     /start
     ```



