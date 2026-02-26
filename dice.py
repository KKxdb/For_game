from flask import Flask, request
import random
import requests
import threading
import os

app = Flask(__name__)

# Вебхук береться з Environment Variable
WEBHOOK = os.environ.get("WEBHOOK_URL")

def check_roll(skill, roll, difficulty):
    """Перевірка успіху за складністю"""
    if difficulty == "hard":
        target = skill // 2
    elif difficulty == "extreme":
        target = skill // 5
    else:
        target = skill
    return roll <= target

def send_to_discord(message):
    """Асинхронна відправка повідомлення в Discord"""
    try:
        requests.post(WEBHOOK, json={"content": message})
    except Exception as e:
        print("Discord webhook error:", e)

@app.route("/roll", methods=["POST", "GET"])
def roll():
    try:
        skill = int(request.values.get("skill", 0))
    except ValueError:
        skill = 0
    difficulty = request.values.get("difficulty", "normal")
    skill_name = request.values.get("skill_name", "Навичка")
    character_name = request.values.get("character_name", "Персонаж")

    roll_value = random.randint(1, 100)

    # критичний успіх та фумбл
    if roll_value == 1:
        result = "Критичний успіх 🎯"
    elif roll_value == 100:
        result = "Фумбл 💀"
    else:
        success = check_roll(skill, roll_value, difficulty)
        result = "Успіх ✅" if success else "Провал ❌"

    message = (
        f"🎲 {skill_name} ({character_name})\n"
        f"Складність: {difficulty}\n"
        f"Навичка: {skill}\n"
        f"Кидок: {roll_value}\n"
        f"Результат: {result}"
    )

    # асинхронна відправка
    threading.Thread(target=send_to_discord, args=(message,)).start()

    return "OK"

# Додатковий маршрут для пінгу / перевірки живого сервісу
@app.route("/")
def home():
    return "alive"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)