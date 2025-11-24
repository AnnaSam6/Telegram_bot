from config.database import db

def insert_initial_data():
    """Добавление начальных данных в базу"""
    connection = db.connect()
    cursor = connection.cursor()
    
    # Вставляем слова
    all_words = level_1_words + level_2_words + level_3_words + level_4_words
    for word_data in all_words:
        cursor.execute(
            "INSERT INTO words (word, translation, level) VALUES (%s, %s, %s)",
            (word_data['word'], word_data['translation'], word_data['level'])
        )
    
    # Вставляем предложения
    all_sentences = (level_1_sentences + level_2_sentences + 
                    level_3_sentences + level_4_sentences)
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
