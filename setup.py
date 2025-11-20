import psycopg2

def setup_database():
    try:
        # Подключаемся к созданной базе
        conn = psycopg2.connect(
            host="localhost",
            database="vocabulary_bot",
            user="postgres",
            password="200296"  # ← тот пароль, которым вошли в pgAdmin
        )
        
        cursor = conn.cursor()
        
        # Создаем таблицы
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS common_words (
                id SERIAL PRIMARY KEY,
                russian_word VARCHAR(100) NOT NULL,
                english_word VARCHAR(100) NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS user_words (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                russian_word VARCHAR(100) NOT NULL,
                english_word VARCHAR(100) NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id BIGINT PRIMARY KEY,
                correct_answers INTEGER DEFAULT 0,
                total_answers INTEGER DEFAULT 0
            )
            '''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Добавляем общие слова
        common_words = [
            ('красный', 'red'), ('синий', 'blue'), ('зеленый', 'green'),
            ('я', 'I'), ('ты', 'you'), ('он', 'he'), ('она', 'she'),
            ('дом', 'house'), ('кот', 'cat'), ('собака', 'dog')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM common_words")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO common_words (russian_word, english_word) VALUES (%s, %s)",
                common_words
            )
            print("✅ Общие слова добавлены")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 База данных настроена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    setup_database()