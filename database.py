from sqlalchemy import create_engine, Column, String, Time
from sqlalchemy.orm import declarative_base, sessionmaker
from config import SQLALCHEMY_DATABASE_URL

# Создаем подключение к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель пользователя с временем напоминания
class User(Base):
    __tablename__ = "users"
    chat_id = Column(String, primary_key=True)
    reminder_time = Column(Time, nullable=True)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 