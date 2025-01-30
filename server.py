from flask import Flask  
import os  
import bot  # Impor file bot agar berjalan otomatis
import threading
import requests
import time

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

if __name__ == "__main__":  
    threading.Thread(target=keep_alive, daemon=True).start()  # Keep-alive thread
    threading.Thread(target=run_bot, daemon=True).start()  # Thread untuk bot Telegram
    
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)  # Jalankan Flask
