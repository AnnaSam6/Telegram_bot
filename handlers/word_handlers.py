from telebot import types
from services.data_repository import DataRepository
from services.bot_service import BotService

class WordHandlers:
    def __init__(self, bot):
        self.bot = bot
        self.data_repo = DataRepository()
        self.bot_service = BotService()

    def handle_words_start(self, message):
        """Начало изучения слов"""
        user_id = message.from_user.id
        user = self.data_repo.get_or_create_user(
            user_id, 
            message.from_user.username, 
            message.from_user.first_name
        )
        
        # Получаем случайное слово
        word = self.data_repo.get_random_word(user['level'] if user else 1)
        
        if not word:
            self.bot.send_message(
                message.chat.id,
                "❌ Не найдено слов для изучения",
                reply_markup=self.bot_service.create_main_menu()
            )
            return

        # Получаем варианты ответов
        options = self.data_repo.get_word_options(word['id'], word['level'])
        
        # Создаем клавиатуру
        markup = self.bot_service.create_word_options_keyboard(options)
        
        # Отправляем вопрос
        self.bot.send_message(
            message.chat.id,
            f"🇷🇺 Выберите перевод слова: **{word['translation']}**",
            parse_mode='Markdown',
            reply_markup=markup
        )

    def handle_word_answer(self, message):
        """Обработка ответа пользователя"""
        # Здесь должна быть логика проверки ответа
        # Пока просто отправляем в главное меню
        from handlers.user_handlers import UserHandlers
        user_handlers = UserHandlers(self.bot)
        user_handlers.handle_main_menu(message)
