from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from pydantic import BaseModel

# URL базы данных для SQLite
DATABASE_URL = "sqlite:///./logs.db"  # Для SQLite

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определение базового класса для моделей
Base = declarative_base()


class Log(Base):
    """
    Модель для хранения логов.

    Attributes:
        id (int): Уникальный идентификатор записи.
        user_id (int): ID пользователя, который отправил команду.
        command (str): Команда, отправленная пользователем.
        timestamp (datetime): Время создания записи лога (по умолчанию текущее время).
        response (str): Ответ бота на команду пользователя.
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    command = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    response = Column(String)


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, primary_key=True)  # ID пользователя
    preferred_city = Column(String)  # Предпочитаемый город


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)


# Pydantic модель для создания логов через FastAPI
class LogCreate(BaseModel):
    """
    Модель для создания новых записей логов.

    Attributes:
        user_id (int): ID пользователя.
        command (str): Команда, отправленная пользователем.
        response (str): Ответ бота на команду пользователя.
    """
    user_id: int
    command: str
    response: str


class LogResponse(LogCreate):
    """
    Модель для представления записей логов с дополнительными полями.

    Attributes:
        id (int): Уникальный идентификатор записи.
        timestamp (datetime): Время создания записи лога.

    Config:
        from_attributes (bool): Позволяет Pydantic работать с SQLAlchemy моделями.
    """
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True  # Позволяет Pydantic работать с SQLAlchemy моделями
