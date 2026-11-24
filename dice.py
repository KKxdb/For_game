from flask import Flask, request
import random
import requests
import threading
import os
from PIL import Image
import io
import re

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

@app.route("/upload-photo", methods=["POST"])
def upload_photo():
    try:
        data = request.get_data()

        if not data:
            return "No data received", 400

        if len(data) > 10 * 1024 * 1024:
            return "File too large", 413

        # Временно сохраняем полученные данные
        with open("/tmp/last_image_field.fdf", "wb") as f:
            f.write(data)

        print("Received content type:", request.content_type)
        print("Received data size:", len(data))
        print("Received header:", data[:30])

        return "FDF received successfully", 200

    except Exception as e:
        print("Upload error:", e)
        return "Upload error", 500


@app.route("/upload-image", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()

        if not data:
            return "No JSON received", 400

        width = int(data["width"])
        height = int(data["height"])
        hex_data = data["image"]

        if width <= 0 or height <= 0:
            return "Invalid dimensions", 400

        if width * height > 4000000:
            return "Image too large", 413

        expected_length = width * height * 8

        if len(hex_data) != expected_length:
            return "Invalid HEX length", 400

        if not re.fullmatch(r"[0-9a-fA-F]+", hex_data):
            return "Invalid HEX data", 400

        # HEX -> bytes
        argb = bytes.fromhex(hex_data)

        # ARGB -> RGBA
        rgba = bytearray(len(argb))

        for i in range(0, len(argb), 4):
            a, r, g, b = argb[i:i+4]
            rgba[i:i+4] = bytes([r, g, b, a])

        # Создаём PNG
        image = Image.frombytes(
            "RGBA",
            (width, height),
            bytes(rgba)
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        if not WEBHOOK:
            return "WEBHOOK_URL not found", 500

        # Отправляем фотографию в Discord
        response = requests.post(
            WEBHOOK,
            data={"content": "📷 Фото из PDF"},
            files={
                "file": ("hero.png", buffer, "image/png")
            },
            timeout=30
        )

        print("Discord image status:", response.status_code)
        print("Discord response:", response.text)

        if response.status_code not in (200, 204):
            return "Discord upload failed", 502

        return {
            "status": "success",
            "message": "Image sent to Discord"
        }, 200

    except Exception as e:
        print("Image upload error:", e)
        return str(e), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)