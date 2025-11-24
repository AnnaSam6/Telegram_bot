from config.database import db

class DataRepository:
    def get_or_create_user(self, user_id, username, first_name):
        connection = db.connect()
        cursor = connection.cursor()
        
        # Проверяем есть ли пользователь
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Создаем нового пользователя
            cursor.execute(
                "INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s)",
                (user_id, username, first_name)
            )
            connection.commit()
        
        cursor.close()
        connection.close()
        return user

    def get_random_word(self, level=1):
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute(
            "SELECT * FROM words WHERE level = %s ORDER BY RANDOM() LIMIT 1",
            (level,)
        )
        word = cursor.fetchone()
        
        cursor.close()
        connection.close()
        return word
