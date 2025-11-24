import os
from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from handlers.user_handlers import UserHandlers
from handlers.word_handlers import WordHandlers

# Инициализация бота
token_bot = os.getenv('TELEGRAM_TOKEN')
state_storage = StateMemoryStorage()
bot = TeleBot(token_bot, state_storage=state_storage)

# Создаем обработчики
user_handlers = UserHandlers(bot)
word_handlers = WordHandlers(bot)

# Регистрируем команды
@bot.message_handler(commands=['start'])
def start_command(message):
    user_handlers.handle_start(message)

@bot.message_handler(func=lambda message: message.text == '📚 Учить слова')
def words_command(message):
    word_handlers.handle_words_start(message)

@bot.message_handler(func=lambda message: message.text == '🏠 Главное меню')
def main_menu(message):
    user_handlers.handle_main_menu(message)

# Запуск бота
if __name__ == '__main__':
    print('Бот запущен...')
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
