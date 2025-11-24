"""
Сервис для логики обучения и работы с карточками.
"""
import random
from services.data_repository import DataRepository


class LearningService:
    """Сервис для управления процессом обучения."""
    
    def __init__(self):
        """Инициализация сервиса обучения."""
        self.data_repo = DataRepository()

    def create_word_card(self, user_id: int, level: int = 1) -> dict:
        """Создать карточку для изучения слов."""
        user = self.data_repo.get_or_create_user(
            user_id, "user", "User"
        )
        
        word_data = self.data_repo.get_random_word(level)
        
        if not word_data:
            return None

        target_word = word_data[1]
        translate = word_data[2]
        
        other_words_data = self.data_repo.get_word_options(
            word_data[0], level, 4
        )
        others = [word[0] for word in other_words_data]
        
        return {
            'target_word': target_word,
            'translate_word': translate,
            'other_words': others,
            'word_id': word_data[0],
            'user_level': level
        }

    def check_answer(self, user_answer: str, target_word: str) -> bool:
        """Проверить правильность ответа."""
        return user_answer.strip().lower() == target_word.lower()
