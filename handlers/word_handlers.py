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
        
        # Получаем или создаем пользователя
        user = self.data_repo.get_or_create_user(
            user_id, 
            message.from_user.username or "user",
            message.from_user.first_name or "User"
        )
        
        # Получаем уровень пользователя
        level = self.data_repo.get_user_level(user_id)
        
        # Получаем случайное слово
        word = self.data_repo.get_random_word(level)
        
        if not word:
            self.bot.send_message(
                message.chat.id,
                "❌ Не найдено слов для изучения",
                reply_markup=self.bot_service.create_main_menu()
            )
            return

        # Получаем варианты ответов (word[0] - id, word[3] - уровень)
        options = self.data_repo.get_word_options(word[0], word[3])
        
        # Добавляем правильный ответ в варианты (word[1] - английское слово)
        all_options = options + [word[1]]
        
        # Создаем клавиатуру
        markup = self.bot_service.create_word_options_keyboard(all_options)
        
        # Отправляем вопрос (word[2] - перевод)
        self.bot.send_message(
            message.chat.id,
            f"🇷🇺 Выберите перевод слова: **{word[2]}**",
            parse_mode='Markdown',
            reply_markup=markup
        )

    def handle_word_answer(self, message):
        """Обработка ответа пользователя"""
        # Временная заглушка - возврат в главное меню
        from handlers.user_handlers import UserHandlers
        user_handlers = UserHandlers(self.bot)
        user_handlers.handle_main_menu(message)
