from flask import Flask, request
import random
import requests
import os

app = Flask(__name__)

WEBHOOK = os.getenv("WEBHOOK_URL")

def check_roll(skill, roll, difficulty):
    if difficulty == "hard":
        target = skill // 2
    elif difficulty == "extreme":
        target = skill // 5
    else:
        target = skill
    return roll <= target

@app.route("/roll", methods=["POST", "GET"])
def roll():
    skill = int(request.values.get("skill", 0))
    difficulty = request.values.get("difficulty", "normal")
    skill_name = request.values.get("skill_name", "Навичка")

    roll = random.randint(1, 100)
    success = check_roll(skill, roll, difficulty)

    result = "Успіх ✅" if success else "Провал ❌"

    message = (
        f"🎲 {skill_name}\n"
        f"Складність: {difficulty}\n"
        f"Навичка: {skill}\n"
        f"Кидок: {roll}\n"
        f"Результат: {result}"
    )

    requests.post(WEBHOOK, json={"content": message})

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
