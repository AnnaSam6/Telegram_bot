# Создайте services/bot_service.py
from telebot import types

class BotService:
    def create_main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📚 Учить слова')
        btn2 = types.KeyboardButton('📊 Статистика')
        markup.add(btn1, btn2)
        return markup

    def create_word_options_keyboard(self, options):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for option in options:
            markup.add(types.KeyboardButton(option))
        markup.add(types.KeyboardButton('🏠 Главное меню'))
        return markup
