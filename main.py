import random
import os
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

# Импорты сервисов для разделения ответственности
from services.data_repository import DataRepository
from services.learning_service import LearningService


print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = os.getenv('TELEGRAM_TOKEN')  # Токен из .env
bot = TeleBot(token_bot, state_storage=state_storage)

# Инициализация сервисов
data_repo = DataRepository()
learning_service = LearningService()

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    """Показать подсказку."""
    return '\n'.join(lines)


def show_target(data):
    """Показать правильный ответ."""
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    """Команды бота."""
    
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    """Состояния бота."""
    
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    """Получить шаг пользователя."""
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    """Создать карточки для изучения слов."""
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Hello, stranger, let study English...")
    
    # СОЗДАЕМ ИЛИ ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ ИЗ БД
    user = data_repo.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "user",
        message.from_user.first_name or "User"
    )
    
    # ПОЛУЧАЕМ СЛОВО ИЗ БД, А НЕ ЖЕСТКО ЗАКОДИРОВАННОЕ
    level = data_repo.get_user_level(message.from_user.id)
    word_data = data_repo.get_random_word(level)
    
    if not word_data:
        bot.send_message(message.chat.id, "No words available in database")
        return
    
    # word_data[0] - id, word_data[1] - word, word_data[2] - translation
    target_word = word_data[1]  # английское слово из БД
    translate = word_data[2]    # перевод из БД
    
    # ПОЛУЧАЕМ ВАРИАНТЫ ОТВЕТОВ ИЗ БД
    other_words_data = data_repo.get_word_options(word_data[0], level, 4)
    others = [word[0] for word in other_words_data]  # извлекаем слова

    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others
        data['word_id'] = word_data[0]  # сохраняем ID слова для прогресса


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    """Показать следующую карточку."""
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    """Удалить слово из изучения."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        print(f"Delete word: {data['target_word']}")  # TODO: удалить из БД


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    """Добавить новое слово."""
    cid = message.chat.id
    userStep[cid] = 1
    print(f"Add word: {message.text}")  # TODO: сохранить в БД


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    """Обработать ответ пользователя."""
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        
        if text == target_word:
            # ПРАВИЛЬНЫЙ ОТВЕТ - обновляем прогресс в БД
            data_repo.update_word_progress(
                message.from_user.id, 
                data['word_id'], 
                True
            )
            
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            # НЕПРАВИЛЬНЫЙ ОТВЕТ - обновляем прогресс в БД
            if 'word_id' in data:
                data_repo.update_word_progress(
                    message.from_user.id, 
                    data['word_id'], 
                    False
                )
            
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint(
                "Допущена ошибка!",
                f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}"
            )
    
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
