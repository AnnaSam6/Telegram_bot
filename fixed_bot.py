# === КОД ДЛЯ RENDER === 
from flask import Flask
import threading
import requests
import time

# Создаем Flask приложение для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 MyEnglishBot is running! Telegram: @MyInglishbot"

@app.route('/health')
def health():
    return "OK"

def run_web():
    app.run(host='0.0.0.0', port=3000)

# Функция для поддержания активности (РЕШАЕТ ПРОБЛЕМУ "ЗАСЫПАНИЯ")
def keep_alive():
    while True:
        try:
            # Будим наш же сервис каждые 4 минуты
            requests.get('https://myenglishbot-sjwc.onrender.com', timeout=10)
            print("✅ Keep-alive: сервис активен")
        except Exception as e:
            print(f"⚠️ Keep-alive ошибка: {e}")
        time.sleep(240)  # 4 минуты

# Запускаем Flask в отдельном потоке
print("🚀 Starting Flask server for Render...")
web_thread = threading.Thread(target=run_web, daemon=True)
web_thread.start()

# Запускаем авто-пробуждение
print("🔧 Starting keep-alive service...")
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

print("✅ Flask server started in background")
print("✅ Keep-alive service started")
# === КОНЕЦ КОДА ДЛЯ RENDER === 

import urllib.request
import json
import random
import os
from datetime import datetime

class MessageTracker:
    def __init__(self):
        self.processed_updates = set()
        self.lock = threading.Lock()
        # Улучшенная защита от дублей
        self.user_last_action = {}
        self.last_callback_data = {}
        self.cooldown = 1.5  # секунды
    
    def is_processed(self, update_id):
        with self.lock:
            return update_id in self.processed_updates
    
    def mark_processed(self, update_id):
        with self.lock:
            self.processed_updates.add(update_id)
            if len(self.processed_updates) > 1000:
                self.processed_updates = set(list(self.processed_updates)[-500:])
    
    def can_process_user(self, user_id, action_type="message"):
        current_time = time.time()
        with self.lock:
            user_key = f"{user_id}_{action_type}"
            
            if user_key in self.user_last_action:
                time_diff = current_time - self.user_last_action[user_key]
                if time_diff < self.cooldown:
                    return False
            
            self.user_last_action[user_key] = current_time
            return True
    
    def is_duplicate_callback(self, user_id, callback_data):
        current_time = time.time()
        with self.lock:
            user_key = f"{user_id}_callback"
            
            if user_key in self.last_callback_data:
                last_data, last_time = self.last_callback_data[user_key]
                if last_data == callback_data and (current_time - last_time) < 3:
                    return True
            
            self.last_callback_data[user_key] = (callback_data, current_time)
            return False

message_tracker = MessageTracker()

class FixedEnglishBot:
    def __init__(self, token):
        self.token = token
        self.data_file = "english_data.json"
        self.load_data()
        # Храним последние вопросы для каждого пользователя
        self.user_questions = {}
        # Храним состояние добавления слов
        self.user_adding_word = {}
        # Кэш слов для каждого пользователя
        self.user_words_cache = {}
        # Время последней активности
        self.last_activity = {}
        # Счетчик ошибок для самовосстановления
        self.error_count = 0
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "common_words": {
                    "красный": "red", "синий": "blue", "зеленый": "green",
                    "я": "I", "ты": "you", "он": "he", "она": "she",
                    "дом": "house", "кот": "cat", "собака": "dog",
                    "мама": "mother", "папа": "father", "вода": "water",
                    "еда": "food", "стол": "table", "стул": "chair"
                },
                "user_words": {},
                "user_stats": {}
            }
            self.save_data()
        print("✅ Данные загружены")
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
    
    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            if reply_markup:
                data["reply_markup"] = reply_markup
            
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.error_count = 0  # Сбрасываем счетчик ошибок при успехе
                return json.loads(response.read().decode())
        except Exception as e:
            self.error_count += 1
            print(f"❌ Ошибка отправки ({self.error_count}): {e}")
            
            # Если много ошибок подряд - делаем паузу
            if self.error_count > 5:
                print("⚠️ Много ошибок, делаем паузу 10 секунд...")
                time.sleep(10)
                
            return None
    
    def get_user_words(self, user_id):
        user_id_str = str(user_id)
        
        # Используем кэш для ускорения
        if user_id in self.user_words_cache:
            return self.user_words_cache[user_id]
        
        common_words = list(self.data["common_words"].items())
        
        if user_id_str in self.data["user_words"]:
            user_words = list(self.data["user_words"][user_id_str].items())
        else:
            user_words = []
        
        all_words = common_words + user_words
        self.user_words_cache[user_id] = all_words
        return all_words
    
    def generate_question(self, user_id):
        words = self.get_user_words(user_id)
        if not words:
            return None
        
        # Обновляем время активности
        self.last_activity[user_id] = time.time()
        
        # Выбираем слово, отдавая предпочтение тем, что реже спрашивались
        russian_word, correct_answer = random.choice(words)
        
        all_english_words = list(set([eng for rus, eng in words]))
        if len(all_english_words) < 4:
            # Если слов мало, добавляем стандартные варианты
            standard_words = ["apple", "book", "home", "time", "word", "day", "man", "way"]
            all_english_words.extend([w for w in standard_words if w not in all_english_words])
        
        wrong_answers = random.sample(
            [w for w in all_english_words if w != correct_answer], 
            min(3, len(all_english_words) - 1)
        )
        
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        question_data = {
            "question": f"Как перевести слово: <b>{russian_word}</b> ?",
            "options": options,
            "correct_answer": correct_answer,
            "russian_word": russian_word,
            "timestamp": time.time(),
            "user_id": user_id
        }
        
        return question_data
    
    def create_keyboard(self, options):
        keyboard = {
            "inline_keyboard": [
                [{"text": option, "callback_data": option}] for option in options
            ]
        }
        return keyboard
    
    def create_main_menu(self):
        keyboard = {
            "keyboard": [
                ["🎓 Учить слова", "📊 Статистика"],
                ["➕ Добавить слово", "🗑️ Удалить слово"],
                ["❓ Помощь", "⚙️ Настройки"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        return keyboard
    
    def create_settings_menu(self):
        keyboard = {
            "keyboard": [
                ["🔙 Назад в меню"],
                ["📝 Изменить сложность", "🔄 Сбросить прогресс"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        return keyboard
    
    def handle_start(self, chat_id, user_id):
        welcome_text = """
🤖 <b>Добро пожаловать в MyEnglishBot!</b>

Я помогу вам учить английские слова!

<b>Используйте кнопки ниже для быстрого доступа:</b>
🎓 Учить слова - начать обучение
📊 Статистика - посмотреть прогресс  
➕ Добавить слово - добавить новое слово
🗑️ Удалить слово - удалить слово
❓ Помощь - справка по боту
⚙️ Настройки - настройки бота
        """
        menu = self.create_main_menu()
        self.send_message(chat_id, welcome_text, menu)
        
        user_id_str = str(user_id)
        if user_id_str not in self.data["user_stats"]:
            self.data["user_stats"][user_id_str] = {
                "correct_answers": 0,
                "total_answers": 0,
                "words_added": 0,
                "last_active": datetime.now().isoformat(),
                "streak": 0
            }
            self.save_data()
    
    def handle_learn(self, chat_id, user_id):
        question_data = self.generate_question(user_id)
        if not question_data:
            self.send_message(chat_id, "📝 У вас пока нет слов для изучения. Добавьте слова с помощью кнопки '➕ Добавить слово'")
            return
        
        keyboard = self.create_keyboard(question_data["options"])
        self.send_message(chat_id, question_data["question"], keyboard)
        
        # Сохраняем вопрос для пользователя ПОСЛЕ отправки
        self.user_questions[user_id] = question_data
        
        print(f"📝 Отправлен вопрос пользователю {user_id}: {question_data['russian_word']} -> {question_data['correct_answer']}")
    
    def handle_answer(self, chat_id, user_id, user_answer, correct_answer):
        user_id_str = str(user_id)
        
        stats = self.data["user_stats"][user_id_str]
        stats["total_answers"] += 1
        stats["last_active"] = datetime.now().isoformat()
        
        if user_answer == correct_answer:
            stats["correct_answers"] += 1
            stats["streak"] = stats.get("streak", 0) + 1
            streak_text = f"\n🔥 Серия правильных ответов: {stats['streak']}" if stats["streak"] > 1 else ""
            message = f"✅ <b>Правильно!</b> Отличная работа!{streak_text}\nСлово переводится как: <b>{correct_answer}</b>"
        else:
            stats["streak"] = 0
            message = f"❌ <b>Неправильно.</b> Правильный ответ: <b>{correct_answer}</b>"
        
        self.save_data()
        
        # Сначала отправляем ответ
        self.send_message(chat_id, message)
        
        # Затем сразу отправляем следующий вопрос
        time.sleep(1.5)
        self.handle_learn(chat_id, user_id)
    
    def handle_add_word(self, chat_id, user_id):
        message = """
📝 <b>Добавление нового слова</b>

Отправьте слово в формате:
<code>русское слово - английское слово</code>

Например:
<code>яблоко - apple</code>

После добавления слова вернутся кнопки меню.
        """
        self.send_message(chat_id, message)
    
    def handle_remove_word(self, chat_id, user_id):
        words = self.get_user_words(user_id)
        if not words or len(words) <= len(self.data["common_words"]):
            self.send_message(chat_id, "🗑️ У вас нет пользовательских слов для удаления.")
            return
        
        user_words = [word for word in words if word[0] not in self.data["common_words"]]
        if not user_words:
            self.send_message(chat_id, "🗑️ У вас нет пользовательских слов для удаления.")
            return
        
        # Показываем первые 10 слов для удаления
        word_list = "\n".join([f"• {rus} - {eng}" for rus, eng in user_words[:10]])
        message = f"""
🗑️ <b>Удаление слова</b>

Ваши слова:
{word_list}

Для удаления отправьте:
<code>удалить русское_слово</code>

Например:
<code>удалить яблоко</code>
        """
        self.send_message(chat_id, message)
    
    def remove_user_word(self, user_id, text):
        try:
            if not text.startswith("удалить "):
                return False, "Неверный формат. Используйте: удалить русское_слово"
            
            russian_word = text[8:].strip()
            user_id_str = str(user_id)
            
            if (user_id_str in self.data["user_words"] and 
                russian_word in self.data["user_words"][user_id_str]):
                
                del self.data["user_words"][user_id_str][russian_word]
                # Очищаем кэш
                if user_id in self.user_words_cache:
                    del self.user_words_cache[user_id]
                
                self.save_data()
                return True, f"✅ Слово '<b>{russian_word}</b>' удалено!"
            else:
                return False, f"❌ Слово '<b>{russian_word}</b>' не найдено в вашем словаре"
                
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def add_user_word(self, user_id, text):
        try:
            if ' - ' not in text:
                return False, "Неверный формат. Используйте: русское слово - английское слово"
            
            russian_word, english_word = [word.strip() for word in text.split(' - ', 1)]
            
            # Проверяем валидность слов
            if not russian_word or not english_word:
                return False, "❌ Оба слова должны быть заполнены"
            
            user_id_str = str(user_id)
            if user_id_str not in self.data["user_words"]:
                self.data["user_words"][user_id_str] = {}
            
            self.data["user_words"][user_id_str][russian_word] = english_word
            # Очищаем кэш
            if user_id in self.user_words_cache:
                del self.user_words_cache[user_id]
            
            # Обновляем статистику
            if user_id_str in self.data["user_stats"]:
                self.data["user_stats"][user_id_str]["words_added"] = self.data["user_stats"][user_id_str].get("words_added", 0) + 1
            
            self.save_data()
            
            return True, f"✅ Слово '<b>{russian_word}</b>' -> '<b>{english_word}</b>' добавлено!"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def handle_stats(self, chat_id, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.data["user_stats"]:
            stats = self.data["user_stats"][user_id_str]
            correct = stats["correct_answers"]
            total = stats["total_answers"]
            words_added = stats.get("words_added", 0)
            streak = stats.get("streak", 0)
            
            if total > 0:
                percentage = (correct / total) * 100
                message = f"""
📊 <b>Ваша статистика:</b>

✅ Правильных ответов: {correct}
❌ Всего ответов: {total}
📈 Процент правильных: {percentage:.1f}%
🔥 Текущая серия: {streak}
📝 Добавлено слов: {words_added}
                """
            else:
                message = "📊 У вас пока нет статистики. Начните учить слова с /learn"
        else:
            message = "📊 У вас пока нет статистики. Начните учить слова с /learn"
        
        self.send_message(chat_id, message)
    
    def handle_settings(self, chat_id, user_id):
        message = """
⚙️ <b>Настройки бота</b>

Здесь вы можете настроить работу бота под себя.

Используйте кнопки ниже для управления настройками.
        """
        menu = self.create_settings_menu()
        self.send_message(chat_id, message, menu)
    
    def handle_help(self, chat_id, user_id):
        help_text = """
❓ <b>Помощь по боту</b>

<b>Основные команды:</b>
🎓 Учить слова - начать обучение словам
📊 Статистика - посмотреть ваш прогресс
➕ Добавить слово - добавить новое слово
🗑️ Удалить слово - удалить ваше слово
⚙️ Настройки - настройки бота

<b>Формат добавления слов:</b>
<code>русское слово - английское слово</code>
Например: <code>яблоко - apple</code>

<b>Формат удаления слов:</b>
<code>удалить русское_слово</code>
Например: <code>удалить яблоко</code>

<b>Обучение:</b>
Нажимайте на кнопки с вариантами ответов или пишите перевод слова.

<b>Текстовые команды:</b>
/start - перезапустить бота
/learn - начать обучение
/add_word - добавить слово
/stats - статистика
        """
        self.send_message(chat_id, help_text)

def process_update(bot, update):
    # Добавляем задержку для защиты от дублирования
    time.sleep(0.2)
    
    update_id = update.get("update_id")
    
    # Проверяем не обрабатывали ли уже этот update
    if message_tracker.is_processed(update_id):
        print(f"⏩ Пропущен дубликат update_id: {update_id}")
        return
    
    # Помечаем как обработанный
    message_tracker.mark_processed(update_id)
    
    try:
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            
            # ЗАЩИТА ОТ ДУБЛЕЙ - проверяем можно ли обрабатывать пользователя
            if not message_tracker.can_process_user(user_id, "message"):
                print(f"⏩ Пропущено быстрое сообщение от пользователя {user_id}")
                return
            
            if "text" in message:
                text = message["text"]
                print(f"📨 Получено сообщение от {user_id}: {text}")
                
                if text == "/start":
                    bot.handle_start(chat_id, user_id)
                elif text == "/learn" or text == "🎓 Учить слова":
                    bot.handle_learn(chat_id, user_id)
                elif text == "/add_word" or text == "➕ Добавить слово":
                    bot.user_adding_word[user_id] = True
                    bot.handle_add_word(chat_id, user_id)
                elif text == "/stats" or text == "📊 Статистика":
                    bot.handle_stats(chat_id, user_id)
                elif text == "🗑️ Удалить слово":
                    bot.handle_remove_word(chat_id, user_id)
                elif text == "⚙️ Настройки":
                    bot.handle_settings(chat_id, user_id)
                elif text == "🔙 Назад в меню":
                    menu = bot.create_main_menu()
                    bot.send_message(chat_id, "Главное меню:", menu)
                elif text == "❓ Помощь":
                    bot.handle_help(chat_id, user_id)
                else:
                    # ПРОВЕРЯЕМ: если пользователь добавляет слово
                    if user_id in bot.user_adding_word and bot.user_adding_word[user_id]:
                        success, response = bot.add_user_word(user_id, text)
                        bot.send_message(chat_id, response)
                        bot.user_adding_word[user_id] = False
                        menu = bot.create_main_menu()
                        bot.send_message(chat_id, "Что дальше?", menu)
                    # Проверяем удаление слова
                    elif text.startswith("удалить "):
                        success, response = bot.remove_user_word(user_id, text)
                        bot.send_message(chat_id, response)
                        menu = bot.create_main_menu()
                        bot.send_message(chat_id, "Что дальше?", menu)
                    # Если есть активный вопрос
                    elif user_id in bot.user_questions:
                        question_data = bot.user_questions[user_id]
                        correct_answer = question_data["correct_answer"]
                        
                        print(f"🔔 Получен текстовый ответ от {user_id}: {text}")
                        # УДАЛЯЕМ вопрос ДО обработки ответа
                        del bot.user_questions[user_id]
                        bot.handle_answer(chat_id, user_id, text, correct_answer)
                    else:
                        # Если нет активного вопроса
                        success, response = bot.add_user_word(user_id, text)
                        if success:
                            menu = bot.create_main_menu()
                            bot.send_message(chat_id, "Что дальше?", menu)
                        else:
                            bot.send_message(chat_id, response)
        
        elif "callback_query" in update:
            callback = update["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            user_id = callback["from"]["id"]
            user_answer = callback["data"]
            
            print(f"🔔 Получен callback от {user_id}: {user_answer}")
            
            # ЗАЩИТА ОТ ДУБЛЕЙ ДЛЯ CALLBACK
            if message_tracker.is_duplicate_callback(user_id, user_answer):
                print(f"⏩ Пропущен дубликат callback от {user_id}: {user_answer}")
                return
            
            if not message_tracker.can_process_user(user_id, "callback"):
                print(f"⏩ Пропущен быстрый callback от {user_id}")
                return
            
            if user_id in bot.user_questions:
                question_data = bot.user_questions[user_id]
                correct_answer = question_data["correct_answer"]
                
                print(f"🔍 Проверяем: {question_data['russian_word']} -> {correct_answer}")
                # УДАЛЯЕМ вопрос ДО обработки ответа - это важно!
                del bot.user_questions[user_id]
                bot.handle_answer(chat_id, user_id, user_answer, correct_answer)
            else:
                print(f"❌ Не найден сохраненный вопрос для пользователя {user_id}")
                bot.send_message(chat_id, "❌ Ошибка: вопрос устарел. Начните заново с /learn")
    
    except Exception as e:
        print(f"❌ Критическая ошибка в process_update: {e}")

if __name__ == "__main__":
    TOKEN = "8592084875:AAFBKu2uXiobygwkSjgfVv8DaFymcISTQp0"
    
    print("🤖 Запуск улучшенного MyEnglishBot...")
    print("✅ Авто-пробуждение активировано")
    print("✅ Защита от дублей активирована")
    print("✅ Система самовосстановления активна")
    
    # Очистка webhook
    try:
        clear_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"
        urllib.request.urlopen(clear_url)
        print("✅ Webhook очищен")
    except:
        print("⚠️ Webhook не очищен, но продолжаем...")
    
    bot = FixedEnglishBot(TOKEN)
    print("🤖 Улучшенный MyEnglishBot запущен...")
    
    last_update_id = 0
    error_count = 0
    
    while True:
        try:
            # Увеличиваем timeout и добавляем параметры
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30&limit=100"
            with urllib.request.urlopen(url, timeout=35) as response:
                data = json.loads(response.read().decode())
            
            if data["ok"]:
                if data["result"]:
                    for update in data["result"]:
                        process_update(bot, update)
                        last_update_id = update["update_id"]
                    error_count = 0  # Сбрасываем счетчик ошибок при успехе
                else:
                    # Нет новых сообщений - это нормально
                    pass
            else:
                print(f"⚠️ Telegram API error: {data}")
                error_count += 1
            
            # Если много ошибок подряд - увеличиваем паузу
            sleep_time = 0.1 if error_count == 0 else min(error_count * 5, 30)
            time.sleep(sleep_time)
            
        except urllib.error.HTTPError as e:
            if e.code == 409:
                print("🔧 Конфликт webhook - очищаем...")
                try:
                    clear_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
                    urllib.request.urlopen(clear_url)
                    print("✅ Webhook очищен")
                except:
                    pass
            else:
                print(f"❌ HTTP Error {e.code}: {e}")
            error_count += 1
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Ошибка в основном цикле: {e}")
            error_count += 1
            time.sleep(5)
