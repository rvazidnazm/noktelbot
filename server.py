from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram Aktif!"

if name == "main":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
