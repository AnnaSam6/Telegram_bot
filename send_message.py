import urllib.request
import json

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    
    # Преобразуем данные в JSON
    data_bytes = json.dumps(data).encode('utf-8')
    
    # Создаем запрос
    req = urllib.request.Request(url, data=data_bytes)
    req.add_header('Content-Type', 'application/json')
    
    # Отправляем запрос
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        return result

# Ваши данные
TOKEN = "8592084875:AAFBKu2uXiobygwkSjgfVv8DaFymcISTQp0"
CHAT_ID = 1045252171

# Отправляем тестовое сообщение
result = send_message(TOKEN, CHAT_ID, "Привет! Это тестовое сообщение от бота!")
print("Сообщение отправлено!")
