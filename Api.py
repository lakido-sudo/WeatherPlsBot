from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from Models import Log, SessionLocal, LogResponse
from typing import List

# Создание экземпляра приложения FastAPI
app = FastAPI()


@app.get("/")
async def root():
    """
    Корневой эндпоинт.

    Возвращает приветственное сообщение и инструкции по использованию API.

    Returns:
        dict: Сообщение с приветствием.
    """
    return {"message": "Welcome to the Weather Bot API! Use /logs to view logs."}


@app.get("/logs/", response_model=List[LogResponse])
async def get_logs(skip: int = 0, limit: int = 10):
    """
    Получение списка логов.

    Позволяет получить записи логов с возможностью пагинации.

    Args:
        skip (int): Количество записей, которые нужно пропустить (по умолчанию 0).
        limit (int): Максимальное количество записей для получения (по умолчанию 10).

    Returns:
        List[LogResponse]: Список записей логов.
    """
    db: Session = SessionLocal()  # Создание сессии для работы с базой данных
    logs = db.query(Log).offset(skip).limit(limit).all()  # Запрос логов с учетом пагинации
    db.close()  # Закрытие сессии
    return logs


@app.get("/logs/{user_id}", response_model=List[LogResponse])
async def get_user_logs(user_id: int):
    """
    Получение логов конкретного пользователя.

    Позволяет получить записи логов для указанного пользователя.

    Args:
        user_id (int): ID пользователя, для которого нужно получить логи.

    Raises:
        HTTPException: Если логи не найдены, возвращает статус 404.

    Returns:
        List[LogResponse]: Список записей логов для указанного пользователя.
    """
    db: Session = SessionLocal()  # Создание сессии для работы с базой данных
    logs = db.query(Log).filter(Log.user_id == user_id).all()  # Запрос логов для конкретного пользователя
    db.close()  # Закрытие сессии

    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")  # Обработка случая, когда логи не найдены

    return logs


if __name__ == "__main__":
    import uvicorn

    # Запуск приложения на локальном сервере
    uvicorn.run(app, host="127.0.0.1", port=8000)
