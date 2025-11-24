# MyEnglishBot - Бот для изучения английских слов

## 📖 Описание
Telegram бот для изучения английских слов с интерактивными кнопками и отслеживанием прогресса.

## 🚀 Функциональность
- 📚 Интерактивное изучение слов с кнопками
- 📊 Статистика правильных ответов
- ➕ Добавление пользовательских слов
- 💾 Хранение данных в SQLite базе данных
- 🎯 Простой и интуитивный интерфейс

## 🛠 Установка и запуск

### Требования
- Python 3.7+
- Telegram Bot Token

### 1. Установка зависимостей
```bash
pip install -r requirements.txt

-- Схема базы данных для Telegram бота изучения английского

-- Пользователи
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level INTEGER DEFAULT 1,
    words_learned INTEGER DEFAULT 0,
    sentences_learned INTEGER DEFAULT 0
);

-- Слова по уровням сложности
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word VARCHAR(200) NOT NULL,
    translation VARCHAR(200) NOT NULL,
    level INTEGER NOT NULL,
    part_of_speech VARCHAR(50),
    example TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Предложения по уровням сложности
CREATE TABLE sentences (
    id SERIAL PRIMARY KEY,
    sentence TEXT NOT NULL,
    translation TEXT NOT NULL,
    level INTEGER NOT NULL,
    grammar_topic VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Прогресс изучения слов
CREATE TABLE user_words (
    user_id BIGINT,
    word_id INTEGER,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    next_review TIMESTAMP,
    PRIMARY KEY (user_id, word_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Прогресс изучения предложений
CREATE TABLE user_sentences (
    user_id BIGINT,
    sentence_id INTEGER,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    PRIMARY KEY (user_id, sentence_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (sentence_id) REFERENCES sentences(id)
);
