from flask import Flask, request
import os
import telebot
import threading

# Inisialisasi Flask
app = Flask(__name__)

# Inisialisasi bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Bot Telegram Aktif!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_update = request.get_json()
        print(f"📩 Webhook menerima update: {json_update}")  # Log update dari Telegram
        
        if json_update:
            update = telebot.types.Update.de_json(json_update)
            bot.process_new_updates([update])
            print("✅ Update berhasil diproses oleh bot")  # Log jika berhasil diproses
        
        return "OK", 200
    except Exception as e:
        print(f"❌ Error Webhook: {str(e)}")  # Log error jika terjadi masalah
        return "Internal Server Error", 500

# Fungsi untuk mengatur webhook di thread terpisah
def run_bot():
    bot.remove_webhook()
    bot.set_webhook(url="https://noktelbot.onrender.com/webhook")  # Ganti dengan URL Anda
    print("✅ Webhook berhasil diset")

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()  # Pastikan webhook diatur
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
