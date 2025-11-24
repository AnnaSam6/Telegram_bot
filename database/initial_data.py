from config.database import db

# Уровень 1 - 300 слов
level_1_words = [
    {"word": "be", "translation": "быть", "level": 1},
    {"word": "have", "translation": "иметь", "level": 1},
    {"word": "do", "translation": "делать", "level": 1},
    {"word": "go", "translation": "идти", "level": 1},
    {"word": "get", "translation": "получать", "level": 1},
    {"word": "make", "translation": "делать", "level": 1},
    {"word": "know", "translation": "знать", "level": 1},
    {"word": "think", "translation": "думать", "level": 1},
    {"word": "take", "translation": "брать", "level": 1},
    {"word": "see", "translation": "видеть", "level": 1},
    # ... добавьте остальные 290 слов уровня 1
]

# Уровень 2 - 300 слов
level_2_words = [
    {"word": "achieve", "translation": "достигать", "level": 2},
    {"word": "admire", "translation": "восхищаться", "level": 2},
    {"word": "affect", "translation": "влиять", "level": 2},
    {"word": "agree", "translation": "соглашаться", "level": 2},
    {"word": "allow", "translation": "позволять", "level": 2},
    # ... добавьте остальные 295 слов уровня 2
]

# Уровень 3 - 250 слов
level_3_words = [
    {"word": "comprehensive", "translation": "всесторонний", "level": 3},
    {"word": "contemporary", "translation": "современный", "level": 3},
    {"word": "significant", "translation": "значительный", "level": 3},
    {"word": "fundamental", "translation": "фундаментальный", "level": 3},
    # ... добавьте остальные 246 слов уровня 3
]

# Уровень 4 - 150 слов
level_4_words = [
    {"word": "ubiquitous", "translation": "вездесущий", "level": 4},
    {"word": "paradoxical", "translation": "парадоксальный", "level": 4},
    {"word": "idiosyncratic", "translation": "идиосинкразический", "level": 4},
    # ... добавьте остальные 147 слов уровня 4
]

# Предложения по уровням
level_1_sentences = [
    {"sentence": "I like apples.", "translation": "Мне нравятся яблоки.", "level": 1},
    {"sentence": "She reads books.", "translation": "Она читает книги.", "level": 1},
    # ... добавьте остальные предложения
]

def insert_initial_data():
    """Добавление начальных данных в базу"""
    connection = db.connect()
    cursor = connection.cursor()
    
    # Очищаем таблицы перед добавлением
    cursor.execute("DELETE FROM words")
    cursor.execute("DELETE FROM sentences")
    
    # Вставляем слова
    all_words = level_1_words + level_2_words + level_3_words + level_4_words
    for word_data in all_words:
        cursor.execute(
            "INSERT INTO words (word, translation, level) VALUES (%s, %s, %s)",
            (word_data['word'], word_data['translation'], word_data['level'])
        )
    
    # Вставляем предложения
    all_sentences = level_1_sentences  # добавьте остальные уровни
    for sentence_data in all_sentences:
        cursor.execute(
            "INSERT INTO sentences (sentence, translation, level) VALUES (%s, %s, %s)",
            (sentence_data['sentence'], sentence_data['translation'], sentence_data['level'])
        )
    
    connection.commit()
    cursor.close()
    connection.close()
    print(f"✅ Добавлено {len(all_words)} слов и {len(all_sentences)} предложений!")

if __name__ == '__main__':
    insert_initial_data()
