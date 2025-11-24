"""
Сервис для работы с Telegram Bot API.
"""
from telebot import types


class BotService:
    """Сервис для создания клавиатур и меню бота."""
    
    def create_main_menu(self) -> types.ReplyKeyboardMarkup:
        """Создать главное меню."""
        markup = types.ReplyKeyboardMarkup(
            row_width=2, 
            resize_keyboard=True
        )
        
        words_btn = types.KeyboardButton('📚 Учить слова')
        stats_btn = types.KeyboardButton('📊 Статистика')
        markup.add(words_btn, stats_btn)
        
        return markup

    def create_learning_keyboard(self, options: list) -> types.ReplyKeyboardMarkup:
        """Создать клавиатуру для обучения."""
        markup = types.ReplyKeyboardMarkup(
            row_width=2, 
            resize_keyboard=True
        )
        
        for option in options:
            markup.add(types.KeyboardButton(option))
        
        next_btn = types.KeyboardButton('➡️ Дальше')
        main_btn = types.KeyboardButton('🏠 Главное меню')
        markup.add(next_btn, main_btn)
        
        return markup
