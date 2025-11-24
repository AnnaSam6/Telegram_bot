from config.database import db

def setup_database():
    connection = db.connect()
    cursor = connection.cursor()
    
    # Создаем таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(100),
            first_name VARCHAR(100),
            level INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            word VARCHAR(200) NOT NULL,
            translation VARCHAR(200) NOT NULL,
            level INTEGER NOT NULL
        )
    ''')
    
    # Добавляем тестовые слова
    test_words = [
        ('hello', 'привет', 1),
        ('world', 'мир', 1),
        ('apple', 'яблоко', 1),
        ('book', 'книга', 1)
    ]
    
    for word, translation, level in test_words:
        cursor.execute(
            "INSERT INTO words (word, translation, level) VALUES (%s, %s, %s)",
            (word, translation, level)
        )
    
    connection.commit()
    cursor.close()
    connection.close()
    print("База данных создана!")

if __name__ == '__main__':
    setup_database()
