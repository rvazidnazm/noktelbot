from flask import Flask, request
import os
import bot  # Impor file bot agar berjalan otomatis
import threading
import requests
import time
import telegram

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram Aktif!"

# Fungsi untuk menjaga server tetap hidup (Keep-Alive)
def keep_alive():
    while True:
        try:
            requests.get("https://noktelbot.onrender.com")  # Ganti dengan URL Render-mu
        except Exception as e:
            print(f"Ping gagal: {e}")
        time.sleep(600)  # Ping setiap 10 menit

# Fungsi untuk menjalankan bot di thread terpisah
def run_bot():
    bot.bot.infinity_polling()

# Set webhook (opsional jika menggunakan webhook)
def set_webhook():
    url = f"https://{os.environ.get('RENDER_EXTERNAL_URL')}/webhook"
    bot.bot.set_webhook(url=url)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telegram.Update.de_json(json_str, bot.bot)
    bot.bot.process_new_updates([update])
    return 'ok'

# Tidak perlu panggil app.run(), Gunicorn akan menjalankan ini
if __name__ == "__main__":
    # Pastikan bot hanya dijalankan sekali
    threading.Thread(target=keep_alive, daemon=True).start()  # Keep-alive thread
    threading.Thread(target=run_bot, daemon=True).start()  # Thread untuk bot Telegram

    # Set webhook jika digunakan (hanya jika menggunakan webhook)
    set_webhook()
