from config.database import db

class DataRepository:
    def get_or_create_user(self, user_id, username, first_name):
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute(
                "INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s)",
                (user_id, username, first_name)
            )
            connection.commit()
        
        cursor.close()
        connection.close()
        return user

    def get_word_options(self, exclude_word_id, level, limit=3):
        """Получить варианты ответов для слов"""
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute(
            """SELECT word FROM words 
            WHERE level = %s AND id != %s 
            ORDER BY RANDOM() LIMIT %s""",
            (level, exclude_word_id, limit)
        )
        options = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        return options

    def get_user_level(self, user_id):
        """Получить уровень пользователя"""
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute(
            "SELECT level FROM users WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        return result[0] if result else 1

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

    def update_word_progress(self, user_id, word_id, is_correct):
        """Обновить прогресс изучения слова"""
        connection = db.connect()
        cursor = connection.cursor()
        
        if is_correct:
            cursor.execute(
                """INSERT INTO user_words (user_id, word_id, correct_answers) 
                VALUES (%s, %s, 1) 
                ON CONFLICT (user_id, word_id) 
                DO UPDATE SET correct_answers = user_words.correct_answers + 1""",
                (user_id, word_id)
            )
        else:
            cursor.execute(
                """INSERT INTO user_words (user_id, word_id, wrong_answers) 
                VALUES (%s, %s, 1) 
                ON CONFLICT (user_id, word_id) 
                DO UPDATE SET wrong_answers = user_words.wrong_answers + 1""",
                (user_id, word_id)
            )
        
        connection.commit()
        cursor.close()
        connection.close()
