from telebot import types
from services.data_repository import DataRepository

class UserHandlers:
    def __init__(self, bot):
        self.bot = bot
        self.data_repo = DataRepository()

    def handle_start(self, message):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        # Сохраняем пользователя в БД
        self.data_repo.get_or_create_user(user_id, username, first_name)
        
        # Создаем меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📚 Учить слова')
        btn2 = types.KeyboardButton('📊 Статистика')
        markup.add(btn1, btn2)
        
        self.bot.send_message(
            message.chat.id,
            f"Привет, {first_name}! Выбери действие:",
            reply_markup=markup
        )

    def handle_main_menu(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📚 Учить слова')
        btn2 = types.KeyboardButton('📊 Статистика')
        markup.add(btn1, btn2)
        
        self.bot.send_message(
            message.chat.id,
            "Главное меню:",
            reply_markup=markup
        )
