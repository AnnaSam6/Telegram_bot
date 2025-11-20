import urllib.request
import json
import random
import time
import os

class FixedEnglishBot:
    def __init__(self, token):
        self.token = token
        self.data_file = "english_data.json"
        self.load_data()
        # Храним последние вопросы для каждого пользователя
        self.user_questions = {}
        # Храним состояние добавления слов
        self.user_adding_word = {}
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "common_words": {
                    "красный": "red", "синий": "blue", "зеленый": "green",
                    "я": "I", "ты": "you", "он": "he", "она": "she",
                    "дом": "house", "кот": "cat", "собака": "dog"
                },
                "user_words": {},
                "user_stats": {}
            }
            self.save_data()
        print("✅ Данные загружены")
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
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
            
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return None
    
    def get_user_words(self, user_id):
        user_id_str = str(user_id)
        common_words = list(self.data["common_words"].items())
        
        if user_id_str in self.data["user_words"]:
            user_words = list(self.data["user_words"][user_id_str].items())
        else:
            user_words = []
        
        return common_words + user_words
    
    def generate_question(self, user_id):
        words = self.get_user_words(user_id)
        if not words:
            return None
        
        russian_word, correct_answer = random.choice(words)
        
        all_english_words = [eng for rus, eng in words]
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
            "timestamp": time.time()
        }
        
        return question_data
    
    def create_keyboard(self, options):
        keyboard = {
            "inline_keyboard": [
                [{"text": option, "callback_data": option}] for option in options
            ]
        }
        return keyboard
    
    def handle_start(self, chat_id, user_id):
        welcome_text = """
🤖 <b>Добро пожаловать в MyEnglishBot!</b>

Я помогу вам учить английские слова!

<b>Доступные команды:</b>
/start - начать работу
/learn - начать обучение
/add_word - добавить новое слово
/stats - посмотреть статистику

Нажмите /learn чтобы начать!
        """
        self.send_message(chat_id, welcome_text)
        
        user_id_str = str(user_id)
        if user_id_str not in self.data["user_stats"]:
            self.data["user_stats"][user_id_str] = {
                "correct_answers": 0,
                "total_answers": 0
            }
            self.save_data()
    
    def handle_learn(self, chat_id, user_id):
        question_data = self.generate_question(user_id)
        if not question_data:
            self.send_message(chat_id, "У вас пока нет слов для изучения. Добавьте слова с помощью /add_word")
            return
        
        keyboard = self.create_keyboard(question_data["options"])
        self.send_message(chat_id, question_data["question"], keyboard)
        
        # Сохраняем вопрос для пользователя ПОСЛЕ отправки
        self.user_questions[user_id] = question_data
        
        print(f"📝 Отправлен вопрос: {question_data['russian_word']} -> {question_data['correct_answer']}")
        print(f"💾 Сохранен вопрос для пользователя {user_id}")
    
    def handle_answer(self, chat_id, user_id, user_answer, correct_answer):
        user_id_str = str(user_id)
        
        stats = self.data["user_stats"][user_id_str]
        stats["total_answers"] += 1
        
        if user_answer == correct_answer:
            stats["correct_answers"] += 1
            message = f"✅ <b>Правильно!</b> Отличная работа!\nСлово переводится как: <b>{correct_answer}</b>"
        else:
            message = f"❌ <b>Неправильно.</b> Правильный ответ: <b>{correct_answer}</b>"
        
        self.save_data()
        
        # Сначала отправляем ответ
        self.send_message(chat_id, message)
        
        # Затем сразу отправляем следующий вопрос
        time.sleep(1)
        self.handle_learn(chat_id, user_id)
    
    def handle_add_word(self, chat_id, user_id):
        message = """
📝 <b>Добавление нового слова</b>

Отправьте слово в формате:
<code>русское слово - английское слово</code>

Например:
<code>яблоко - apple</code>
        """
        self.send_message(chat_id, message)
    
    def add_user_word(self, user_id, text):
        try:
            if ' - ' not in text:
                return False, "Неверный формат. Используйте: русское слово - английское слово"
            
            russian_word, english_word = [word.strip() for word in text.split(' - ', 1)]
            
            user_id_str = str(user_id)
            if user_id_str not in self.data["user_words"]:
                self.data["user_words"][user_id_str] = {}
            
            self.data["user_words"][user_id_str][russian_word] = english_word
            self.save_data()
            
            return True, f"✅ Слово '<b>{russian_word}</b>' добавлено!"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"
    
    def handle_stats(self, chat_id, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.data["user_stats"]:
            stats = self.data["user_stats"][user_id_str]
            correct = stats["correct_answers"]
            total = stats["total_answers"]
            
            if total > 0:
                percentage = (correct / total) * 100
                message = f"""
📊 <b>Ваша статистика:</b>

✅ Правильных ответов: {correct}
❌ Всего ответов: {total}
📈 Процент правильных: {percentage:.1f}%
                """
            else:
                message = "📊 У вас пока нет статистики. Начните учить слова с /learn"
        else:
            message = "📊 У вас пока нет статистики. Начните учить слова с /learn"
        
        self.send_message(chat_id, message)

def process_update(bot, update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        
        if "text" in message:
            text = message["text"]
            
            if text == "/start":
                bot.handle_start(chat_id, user_id)
            elif text == "/learn":
                bot.handle_learn(chat_id, user_id)
            elif text == "/add_word":
                # Устанавливаем состояние "добавление слова"
                bot.user_adding_word[user_id] = True
                bot.handle_add_word(chat_id, user_id)
            elif text == "/stats":
                bot.handle_stats(chat_id, user_id)
            else:
                # ПРОВЕРЯЕМ: если пользователь добавляет слово
                if user_id in bot.user_adding_word and bot.user_adding_word[user_id]:
                    # Это добавление слова, а не ответ на вопрос
                    success, response = bot.add_user_word(user_id, text)
                    bot.send_message(chat_id, response)
                    # Сбрасываем состояние добавления слова
                    bot.user_adding_word[user_id] = False
                # Если есть активный вопрос И мы НЕ добавляем слово
                elif user_id in bot.user_questions:
                    question_data = bot.user_questions[user_id]
                    correct_answer = question_data["correct_answer"]
                    
                    print(f"🔔 Получен текстовый ответ: {text} от пользователя {user_id}")
                    print(f"🔍 Проверяем: {question_data['russian_word']} -> {correct_answer}, ответ: {text}")
                    
                    # Удаляем вопрос ПЕРЕД обработкой
                    del bot.user_questions[user_id]
                    
                    bot.handle_answer(chat_id, user_id, text, correct_answer)
                else:
                    # Если нет активного вопроса и не добавляем слово
                    success, response = bot.add_user_word(user_id, text)
                    bot.send_message(chat_id, response)
    
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        user_answer = callback["data"]
        
        print(f"🔔 Получен ответ: {user_answer} от пользователя {user_id}")
        
        # Используем сохраненный вопрос вместо парсинга текста
        if user_id in bot.user_questions:
            question_data = bot.user_questions[user_id]
            correct_answer = question_data["correct_answer"]
            russian_word = question_data["russian_word"]
            
            print(f"🔍 Проверяем: {russian_word} -> {correct_answer}, ответ: {user_answer}")
            
            # ВАЖНО: Удаляем вопрос ПЕРЕД обработкой ответа
            del bot.user_questions[user_id]
            print(f"🗑️ Удален вопрос для пользователя {user_id}")
            
            bot.handle_answer(chat_id, user_id, user_answer, correct_answer)
        else:
            print(f"❌ Не найден сохраненный вопрос для пользователя {user_id}")
            print(f"📊 Текущие сохраненные вопросы: {list(bot.user_questions.keys())}")
            bot.send_message(chat_id, "❌ Ошибка: вопрос устарел. Начните заново с /learn")

if __name__ == "__main__":
    TOKEN = "8592084875:AAFBKu2uXiobygwkSjgfVv8DaFymcISTQp0"
    
    bot = FixedEnglishBot(TOKEN)
    print("🤖 Fixed MyInglishBot запущен...")
    
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            if data["ok"] and data["result"]:
                for update in data["result"]:
                    process_update(bot, update)
                    last_update_id = update["update_id"]
                    print(f"📨 Обработано сообщение: {last_update_id}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

