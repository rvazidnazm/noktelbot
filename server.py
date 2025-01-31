from flask import Flask, request
import os
import bot  # Pastikan bot.py sudah mengatur bot tanpa polling
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram Aktif!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_update = request.get_json()
    bot.bot.process_new_updates([telebot.types.Update.de_json(json_update)])
    return "OK", 200

if __name__ == "__main__":
    bot.bot.remove_webhook()
    bot.bot.set_webhook(url="https://noktelbot.onrender.com/webhook")  # Ganti dengan URL Anda
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
