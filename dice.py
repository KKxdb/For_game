from flask import Flask, request
import random
import requests
import threading
import os

app = Flask(__name__)

WEBHOOK = os.environ.get("WEBHOOK_URL")

def check_roll(skill, roll, difficulty):
    if difficulty == "hard":
        target = skill // 2
    elif difficulty == "extreme":
        target = skill // 5
    else:
        target = skill
    return roll >= target

def send_to_discord(message):
    if not WEBHOOK:
        print("❌ WEBHOOK_URL not found!")
        return

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(
            WEBHOOK,
            json={"content": message},
            headers=headers,
            timeout=10
        )
        print("Discord status:", response.status_code)
        print("Discord response:", response.text)
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

    roll_value = random.randint(1, 10)

    success = check_roll(skill, roll_value, difficulty)
    result = "Успіх ✅" if success else "Провал ❌"

    message = (
        f"🎲 {skill_name} ({character_name})\n"
        f"Складність: {difficulty}\n"
        f"Навичка: {skill}\n"
        f"Кидок: {roll_value}\n"
        f"Результат: {result}"
    )

    send_to_discord(message)

    return "OK"

@app.route("/")
def home():
    return "alive"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)