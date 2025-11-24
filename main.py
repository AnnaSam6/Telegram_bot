import os
import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from services.data_repository import DataRepository


print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = '8592084875:AAFBKu2uXiobygwkSjgfVv8DaFymcISTQp0'
bot = TeleBot(token_bot, state_storage=state_storage)

# Инициализация репозитория для работы с БД
data_repo = DataRepository()

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    """Показать подсказку пользователю."""
    return '\n'.join(lines)


def show_target(data):
    """Показать правильный перевод."""
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    """Класс для хранения команд бота."""
    
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    """Группа состояний бота."""
    
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    """Получить текущий шаг пользователя."""
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    """Создать карточку для изучения слов."""
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Hello, stranger, let study English...")
    
    # СОЗДАЕМ/ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ В БД
    user = data_repo.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "user",
        message.from_user.first_name or "User"
    )
    
    # ПОЛУЧАЕМ СЛОВО ИЗ БД
    word_data = data_repo.get_random_word(1)  # уровень 1 для начала
    
    if word_data:
        # Используем данные из БД
        target_word = word_data[1]  # английское слово
        translate = word_data[2]    # перевод
        # Получаем варианты из БД
        other_words_data = data_repo.get_word_options(
            word_data[0], 1, 4
        )
        others = [word[0] for word in other_words_data]
        word_id = word_data[0]  # сохраняем ID слова
    else:
        # Fallback - если БД пустая
        target_word = 'Peace'
        translate = 'Мир'
        others = ['Green', 'White', 'Hello', 'Car']
        word_id = None

    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    
    other_words_btns = [
        types.KeyboardButton(word) for word in others
    ]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(
        message.chat.id, 
        greeting, 
        reply_markup=markup
    )
    bot.set_state(
        message.from_user.id, 
        MyStates.target_word, 
        message.chat.id
    )
    
    with bot.retrieve_data(
        message.from_user.id, message.chat.id
    ) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others
        data['word_id'] = word_id  # для обновления прогресса


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    """Показать следующую карточку."""
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    """Удалить слово из изучения."""
    with bot.retrieve_data(
        message.from_user.id, message.chat.id
    ) as data:
        print(f"Delete word from DB: {data['target_word']}")
        # TODO: реализовать удаление из БД


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    """Добавить новое слово в базу."""
    cid = message.chat.id
    userStep[cid] = 1
    print(f"Add word to DB: {message.text}")
    # TODO: реализовать добавление в БД


@bot.message_handler(commands=['restart'])
def restart_bot(message):
    """Перезапустить бота."""
    user_id = message.from_user.id
    
    # Сбрасываем состояние пользователя
    if user_id in known_users:
        known_users.remove(user_id)
    if user_id in userStep:
        userStep[user_id] = 0
    
    bot.send_message(
        message.chat.id,
        "🔄 Бот перезапущен! Начнем заново.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    # Запускаем начальное состояние
    create_cards(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    """Обработать ответ пользователя на слово."""
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    
    with bot.retrieve_data(
        message.from_user.id, message.chat.id
    ) as data:
        target_word = data['target_word']
        
        if text == target_word:
            # ОБНОВЛЯЕМ ПРОГРЕСС В БД
            if data.get('word_id'):
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
            # ОБНОВЛЯЕМ ПРОГРЕСС В БД
            if data.get('word_id'):
                data_repo.update_word_progress(
                    message.from_user.id,
                    data['word_id'],
                    False
                )
            
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            
            hint_text = "Допущена ошибка!"
            hint_desc = (
                f"Попробуй ещё раз вспомнить слово "
                f"🇷🇺{data['translate_word']}"
            )
            hint = show_hint(hint_text, hint_desc)
    
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)


