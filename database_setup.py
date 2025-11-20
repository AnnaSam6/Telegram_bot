import psycopg2

def setup_database():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",  # Подключаемся к основной БД
        user="postgres",
        password="your_password"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Создаем базу данных если не существует
    cursor.execute("CREATE DATABASE vocabulary_bot")
    print("✅ База данных создана")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()