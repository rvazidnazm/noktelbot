from flask import Flask  
import os  

app = Flask(__name__)  

@app.route('/')  
def home():  
    return "Bot Telegram Aktif!"  

if __name__ == "__main__":  # Perbaikan di sini
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
