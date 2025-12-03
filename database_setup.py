"""
Модуль для работы с базой данных.
Поддерживает PostgreSQL (продакшен) и SQLite (разработка).
"""

import os
from contextlib import contextmanager
from typing import Generator, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определяем какую БД использовать
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() == 'true'

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.extensions import connection as PGConnection
    DB_MODULE = psycopg2
else:
    import sqlite3
    from sqlite3 import Connection as SQLiteConnection
    DB_MODULE = sqlite3


class Database:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Инициализация подключения к БД.
        
        Args:
            database_url: URL для подключения к БД (опционально)
        """
        if database_url:
            self.database_url = database_url
        elif USE_POSTGRES:
            self.database_url = os.getenv('DATABASE_URL')
            if not self.database_url:
                raise ValueError("DATABASE_URL не установлен для PostgreSQL")
        else:
            self.database_url = 'vocabulary_bot.db'
    
    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """
        Контекстный менеджер для получения подключения к БД.
        
        Yields:
            Подключение к базе данных
        """
        conn = None
        try:
            if USE_POSTGRES:
                conn = DB_MODULE.connect(
                    self.database_url,
                    cursor_factory=RealDictCursor
                )
            else:
                conn = DB_MODULE.connect(self.database_url)
                conn.row_factory = sqlite3.Row
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, conn: Any) -> Generator[Any, None, None]:
        """
        Контекстный менеджер для получения курсора.
        
        Args:
            conn: Подключение к БД
            
        Yields:
            Курсор для выполнения запросов
        """
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


def init_database() -> None:
    """
    Инициализация базы данных и создание таблиц.
    """
    db = Database()
    
    # SQL для создания таблиц
    create_tables_sql = """
    -- Таблица пользователей
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Таблица стандартных слов (из словаря)
    CREATE TABLE IF NOT EXISTS standard_words (
        id SERIAL PRIMARY KEY,
        english TEXT NOT NULL,
        russian TEXT NOT NULL,
        topic TEXT,
        difficulty_level INTEGER DEFAULT 1,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Таблица пользовательских слов
    CREATE TABLE IF NOT EXISTS user_words (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        english TEXT NOT NULL,
        russian TEXT NOT NULL,
        topic TEXT,
        mastered BOOLEAN DEFAULT FALSE,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    
    -- Таблица статистики изучения
    CREATE TABLE IF NOT EXISTS learning_statistics (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        word_id INTEGER NOT NULL,
        word_type TEXT CHECK(word_type IN ('standard', 'user')),
        correct_attempts INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        last_reviewed TIMESTAMP,
        next_review TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    
    -- Таблица сессий обучения
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        session_type TEXT,
        words_learned INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        total_questions INTEGER DEFAULT 0,
        session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    try:
        with db.get_connection() as conn:
            with db.get_cursor(conn) as cursor:
                # Разделяем SQL на отдельные команды
                commands = create_tables_sql.split(';')
                for command in commands:
                    if command.strip():
                        cursor.execute(command)
        
        logger.info("База данных успешно инициализирована")
        
        # Заполняем стандартные слова, если таблица пуста
        populate_standard_words()
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


def populate_standard_words() -> None:
    """
    Заполнение таблицы стандартными словами.
    """
    standard_words = [
        # Базовые слова
        ("hello", "привет", "basic", 1),
        ("goodbye", "до свидания", "basic", 1),
        ("thank you", "спасибо", "basic", 1),
        ("please", "пожалуйста", "basic", 1),
        
        # Еда
        ("apple", "яблоко", "food", 1),
        ("bread", "хлеб", "food", 1),
        ("water", "вода", "food", 1),
        ("coffee", "кофе", "food", 1),
        
        # Семья
        ("family", "семья", "family", 1),
        ("mother", "мать", "family", 1),
        ("father", "отец", "family", 1),
        ("brother", "брат", "family", 1),
        
        # Работа
        ("work", "работа", "work", 2),
        ("office", "офис", "work", 2),
        ("meeting", "встреча", "work", 2),
        ("project", "проект", "work", 2),
        
        # Путешествия
        ("travel", "путешествие", "travel", 2),
        ("airport", "аэропорт", "travel", 2),
        ("hotel", "отель", "travel", 2),
        ("passport", "паспорт", "travel", 2),
        
        # Технологии
        ("computer", "компьютер", "technology", 3),
        ("internet", "интернет", "technology", 3),
        ("software", "программное обеспечение", "technology", 3),
        ("database", "база данных", "technology", 3),
    ]
    
    db = Database()
    
    try:
        with db.get_connection() as conn:
            with db.get_cursor(conn) as cursor:
                # Проверяем, есть ли уже слова
                cursor.execute("SELECT COUNT(*) as count FROM standard_words")
                result = cursor.fetchone()
                
                if isinstance(result, dict):
                    count = result.get('count', 0) if hasattr(result, 'get') else result[0]
                else:
                    count = result[0] if result else 0
                
                if count == 0:
                    for word in standard_words:
                        if USE_POSTGRES:
                            cursor.execute(
                                """
                                INSERT INTO standard_words 
                                (english, russian, topic, difficulty_level) 
                                VALUES (%s, %s, %s, %s)
                                """,
                                word
                            )
                        else:
                            cursor.execute(
                                """
                                INSERT INTO standard_words 
                                (english, russian, topic, difficulty_level) 
                                VALUES (?, ?, ?, ?)
                                """,
                                word
                            )
                    logger.info(f"Добавлено {len(standard_words)} стандартных слов")
    except Exception as e:
        logger.error(f"Ошибка при заполнении стандартных слов: {e}")
