import telebot
import json
import os
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from datetime import datetime
from telebot import types

# Muat konfigurasi dari file .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Inisialisasi bot
bot = telebot.TeleBot(BOT_TOKEN)

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_users_file_if_not_exists():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as file:
            json.dump([], file)  # Membuat file kosong dengan list kosong

def save_user_state(user_id, state):
    try:
        file_path = "user_state.json"
        data = {}
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        data[str(user_id)] = state
        
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        logging.info(f"✅ Status pengguna {user_id} tersimpan: {state}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan status pengguna: {e}")

def simpan_nomor_pengguna(user_id, nomor):
    try:
        file_path = "user_data.json"
        data = {}
        
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        if str(user_id) not in data:
            data[str(user_id)] = []

        data[str(user_id)].append(nomor)

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        logging.info(f"✅ Nomor {nomor} disimpan untuk user {user_id}")
        return True
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan nomor: {e}")
        return False

# Definisikan user_data di awal skrip
user_data = {}

# ------------------ KHUSUS ADMIN ------------------
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    # Pengecekan ID admin
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "❌ Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    # Ambil teks setelah /broadcast
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.send_message(message.chat.id, "⚠️ Silakan masukkan pesan setelah perintah /broadcast.")
        return

    try:
        # Pastikan file users.json ada
        create_users_file_if_not_exists()  # Membuat file jika belum ada

        # Membaca daftar pengguna dari file users.json
        with open("users.json", "r") as file:
            users = json.load(file)

        sent_count = 0
        failed_count = 0  # Untuk menghitung jumlah pengguna yang gagal menerima pesan

        # Kirim pesan broadcast ke setiap pengguna
        for user in users:
            try:
                bot.send_message(user, f"📢 Pengumuman dari Admin:\n\n{text}", parse_mode="Markdown")
                sent_count += 1
            except Exception as e:
                failed_count += 1
                # Log kesalahan jika gagal mengirim pesan
                print(f"Gagal mengirim pesan ke {user}: {e}")

        # Kirim laporan ke admin
        bot.send_message(ADMIN_ID, f"✅ Pesan berhasil dikirim ke {sent_count} pengguna.\n❌ Gagal mengirim ke {failed_count} pengguna.")
    
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Gagal mengirim broadcast: {str(e)}")

# ------------------ FUNGSI /START ------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)

    try:
        # Pastikan file users.json ada
        if not os.path.exists("users.json"):
            users = []
        else:
            with open("users.json", "r") as file:
                users = json.load(file)

        # Tambahkan pengguna hanya jika belum ada
        if user_id not in users:
            users.append(user_id)
            with open("users.json", "w") as file:
                json.dump(users, file, indent=4)

    except Exception as e:
        print(f"❌ Gagal menambahkan pengguna: {e}")

    # Kirim pesan selamat datang
    nama = message.from_user.first_name
    teks = f"""🙋🏻‍♂️ Selamat datang, {nama}!  

🚀 ZanMi NOKTEL menyediakan nomor luar negeri permanen untuk verifikasi Telegram dengan harga terjangkau!  

🎉 Keuntungan Menggunakan Layanan Kami:  
✅ Verifikasi tanpa batas  
✅ Bisa masuk grup yang diblokir  
✅ Digit nomor cantik  
✅ Nomor fresh, permanen & aman

🚀 Nikmati layanan nomor virtual Telegram kami!
    """

    markup = InlineKeyboardMarkup(row_width=2)  # Mengatur row_width agar tombol Join Channel dan Hubungi Admin berdampingan
    
    # Tombol atas bawah (Beli dan Ketentuan)
    markup.add(InlineKeyboardButton("🛒 Pilih Layanan", callback_data="beli_nomor"))
    markup.add(InlineKeyboardButton("ℹ️ Ketentuan & Cara Pakai", callback_data="info"))
    markup.add(InlineKeyboardButton("📞 Hubungi Admin", url=f"tg://user?id={ADMIN_ID}"))
    
    # Tombol kanan kiri di bawah Ketentuan
    markup.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/zanmistore"), 
               InlineKeyboardButton("🖼️ Channel Testi", url="https://t.me/zanmitestimoni"))
    
    # Mengirim pesan dengan markup
    bot.send_message(message.chat.id, teks, reply_markup=markup, parse_mode="Markdown")

# ------------------ MENU BELI NOMOR ------------------
@bot.callback_query_handler(func=lambda call: call.data == "beli_nomor")
def menu_beli_nomor(call):
    teks = "💳 Layanan Pembelian Nomor\n\nPilih opsi di bawah untuk:\n\n1. Beli Nomor :\nUntuk proses pembelian nomor Telegram.\n\n2. Nomor Saya :\nUntuk melihat nomor yang sudah kamu miliki."
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🛒 Beli Nomor", callback_data="proses_beli"), 
               InlineKeyboardButton("📂 Nomor Saya", callback_data="nomor_saya"))
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="home"))
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ------------------ PROSES PEMBELIAN NOMOR ------------------
@bot.callback_query_handler(func=lambda call: call.data == "proses_beli")
def proses_beli(call):
    teks = "🛒 Beli Nomor\nPilih jenis nomor yang ingin Anda beli :\n\n🌍 : Rp25.000\n🇮🇩 : Rp5.000\n\n🚨 BACA DULU INFORMASI YG DIBAWAH SEBELUM BELI !\n"
    markup = InlineKeyboardMarkup(row_width=2)
        # Tombol kanan kiri di bawah Ketentuan
    markup.add(InlineKeyboardButton("🌍 Nomor Luar Negeri", callback_data="nomor_luar"), 
               InlineKeyboardButton("🇮🇩 Nomor Indonesia", callback_data="nomor_indo"))
    markup.add(InlineKeyboardButton("⚠️ BACA INI DULU !", callback_data="baca_"))
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="beli_nomor"))
    
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ------------------ PROSES PEMBAYARAN NOMOR ------------------

@bot.callback_query_handler(func=lambda call: call.data == "nomor_luar")
def nomor_luar(call):
    # Simpan jenis nomor yang dipilih oleh user
    user_data[call.from_user.id] = {"jenis_nomor": "Nomor Luar Negeri"}

    # Menyimpan jenis nomor yang dipilih ke dalam jenis_nomor.json
    with open("jenis_nomor.json", "w") as file:
        json.dump({"jenis_nomor": "Nomor Luar Negeri"}, file)

    # Lanjutkan ke proses berikutnya (pilih metode pembayaran)
    teks = "💳 Pilih Metode Pembayaran untuk Nomor Luar Negeri:\n\nSilakan pilih metode pembayaran yang diinginkan."
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💳 QRIS", callback_data="bayar_qris"))
    # Tombol kanan kiri di bawah Ketentuan
    markup.add(InlineKeyboardButton("💸 DANA", callback_data="bayar_dana"), 
               InlineKeyboardButton("💳 GoPay", callback_data="bayar_gopay"))
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="proses_beli"))
    
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "nomor_indo")
def nomor_indo(call):
    # Simpan jenis nomor yang dipilih oleh user
    user_data[call.from_user.id] = {"jenis_nomor": "Nomor Indonesia"}

    # Menyimpan jenis nomor yang dipilih ke dalam jenis_nomor.json
    with open("jenis_nomor.json", "w") as file:
        json.dump({"jenis_nomor": "Nomor Indonesia"}, file)

    # Lanjutkan ke proses berikutnya (pilih metode pembayaran)
    teks = "💳 Pilih Metode Pembayaran untuk Nomor Indonesia:\n\nSilakan pilih metode pembayaran yang diinginkan."
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💳 QRIS", callback_data="bayar_qris"))
    # Tombol kanan kiri di bawah Ketentuan
    markup.add(InlineKeyboardButton("💸 DANA", callback_data="bayar_dana"), 
               InlineKeyboardButton("💳 GoPay", callback_data="bayar_gopay"))
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="proses_beli"))
    
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ------------------ NOTIFIKASI PEMBAYARAN KE ADMIN ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("bayar_"))
def pembayaran(call):
    metode = call.data.split("_")[1].upper()
    user_id = call.from_user.id
    nama_pengguna = call.from_user.first_name  # Ambil nama pengguna
    
    # Ambil pilihan jenis nomor yang disimpan di user_data
    pilihan_nomor = user_data.get(user_id, {}).get("jenis_nomor", "Tidak Diketahui")

    teks_admin = f"📢 Pesanan Baru!\n\n👤 Pembeli: {nama_pengguna} (`{user_id}`)\n💳 Metode: {metode}\n📱 Jenis Nomor: {pilihan_nomor}\n\n🔹 Admin, kirim nomor saat konfirmasi!"
    
    markup_admin = InlineKeyboardMarkup()
    markup_admin.add(InlineKeyboardButton("✅ Konfirmasi", callback_data=f"konfirmasi_{user_id}"))
    markup_admin.add(InlineKeyboardButton("❌ Batalkan", callback_data=f"batal_{user_id}"))
    markup_admin.add(InlineKeyboardButton("📩 Hubungi Pembeli", url=f"tg://user?id={user_id}"))
    
    bot.send_message(ADMIN_ID, teks_admin, parse_mode="Markdown", reply_markup=markup_admin)
    bot.edit_message_text("✅ Pesanan dikirim ke admin. Harap tunggu konfirmasi.", call.message.chat.id, call.message.message_id)

# ------------------ ADMIN KONFIRMASI PESANAN ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("konfirmasi_"))
def konfirmasi(call):
    parts = call.data.split("_", 1)
    if len(parts) < 2:
        bot.answer_callback_query(call.id, "❌ Format data tidak valid.", show_alert=True)
        return

    _, user_id = parts  
    user = bot.get_chat(user_id)  # Ambil informasi user

    data = {
        "user_id": user_id,
        "first_name": user.first_name,
        "username": user.username if user.username else "Tidak ada username"
    }

    with open("pending_confirmations.json", "w") as file:
        json.dump(data, file)

    bot.send_message(call.message.chat.id, "✅ Kirim nomor yang akan diberikan ke pembeli.")
    bot.edit_message_text("✅ Menunggu nomor dari admin...", call.message.chat.id, call.message.message_id)

# ------------------ ADMIN BATALKAN PESANAN ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("batal_"))
def batalkan_pesanan(call):
    _, user_id = call.data.split("_")

    bot.send_message(int(user_id), "⚠️ Maaf, pesanan Anda dibatalkan karena stok nomor sedang kosong. Silakan coba lagi nanti atau hubungi admin untuk informasi lebih lanjut.", parse_mode="Markdown")
    bot.edit_message_text("✅ Pesanan berhasil dibatalkan.", call.message.chat.id, call.message.message_id)

# ------------------ ADMIN KIRIM NOMOR KE PEMBELI ------------------
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID)
def simpan_nomor_dari_admin(message):
    try:
        # Membaca file pending_confirmations.json untuk mengambil data pembeli
        with open("pending_confirmations.json", "r") as file:
            data = json.load(file)

        user_id = str(data["user_id"])  # Simpan user_id sebagai string agar sesuai dengan JSON
        nama_pengguna = data.get("first_name", "Tidak Diketahui")
        username_pengguna = data.get("username", "Tidak ada username")

        # Ambil nomor yang dikirim admin
        nomor_terdeteksi = message.text.strip()
        nomor_sensor = f"{nomor_terdeteksi[:3]}xxxxxx{nomor_terdeteksi[-4:]}"  # Sensor nomor untuk privasi

        # Ambil waktu pembelian
        waktu_pembelian = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Simpan nomor ke dalam user_data.json
        try:
            with open("user_data.json", "r") as file:
                user_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            user_data = {}

        # Jika user belum ada di user_data, buat entri baru
        if user_id not in user_data:
            user_data[user_id] = []

        # Simpan hanya nomor ke dalam daftar user
        user_data[user_id].append(nomor_terdeteksi)

        # Simpan kembali ke file
        with open("user_data.json", "w") as file:
            json.dump(user_data, file, indent=4)

        # Kirim notifikasi ke pembeli
        bot.send_message(int(user_id), f"""✅ Pesanan Anda dikonfirmasi!  
📞 Nomor: `{nomor_terdeteksi}`
⏰ Waktu Pembelian: {waktu_pembelian}

⚠️ Harap jangan terminate session yang bernama "PC 64bit loginacc 1.30.0" atau terminate all other sessions, agar Anda tetap bisa menerima OTP.
""", parse_mode="Markdown")

        # Kirim notifikasi ke admin
        bot.send_message(ADMIN_ID, f"""🎉 Transaksi Berhasil Dikonfirmasi!
👤 Pembeli: {nama_pengguna} (`{user_id}`)
💼 Username: {username_pengguna}
📞 Nomor yang Dibeli: {nomor_terdeteksi}
⏰ Waktu Pembelian: {waktu_pembelian}

Terima kasih atas transaksi ini!
""", parse_mode="Markdown")

        # Kirim notifikasi ke channel testimoni dengan data sensor
        channel_id_testimoni = os.getenv("CHANNEL_ID_TESTIMONI")
        bot.send_message(channel_id_testimoni, f"""🎉 User Berhasil Masuk!
👤 Pembeli: {nama_pengguna}
📞 Nomor: {nomor_sensor}
⏰ Waktu Pembelian: {waktu_pembelian}

Terima kasih atas pembelian Anda!
""", parse_mode="Markdown")

        # Kirim notifikasi ke channel pribadi admin dengan data lengkap
        channel_id_pribadi = os.getenv("CHANNEL_ID_PRIBADI")
        bot.send_message(channel_id_pribadi, f"""🎉 Transaksi Berhasil Dikonfirmasi!
👤 Pembeli: {nama_pengguna} (`{user_id}`)
💼 Username: @{username_pengguna}
📞 Nomor yang Dibeli: {nomor_terdeteksi}
⏰ Waktu Pembelian: {waktu_pembelian}

Semua data telah tercatat dengan aman.
""", parse_mode="Markdown")

        # Hapus file pending setelah transaksi selesai
        if os.path.exists("pending_confirmations.json"):
            os.remove("pending_confirmations.json")

        # Konfirmasi ke admin bahwa nomor telah disimpan
        bot.send_message(ADMIN_ID, f"✅ Nomor {nomor_terdeteksi} berhasil dikirim ke pembeli ({nama_pengguna}) dan disimpan di database.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Terjadi kesalahan saat menyimpan nomor.\nError: {str(e)}")


        
# ------------------ MENU NOMOR SAYA ------------------
@bot.callback_query_handler(func=lambda call: call.data == "nomor_saya")
def nomor_saya(call):
    user_id = str(call.from_user.id)

    try:
        # Baca data dari JSON
        if not os.path.exists("user_data.json"):
            data = {}
        else:
            with open("user_data.json", "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}  # Reset jika rusak

        nomor_data = data.get(user_id, [])

        if not nomor_data:
            teks = "📂 Anda belum memiliki nomor yang tersimpan. Atau kalau memang sudah membeli namun nomor tidak ada, bisa pencet tombol di bawah."
            markup = InlineKeyboardMarkup()

            # Tombol Hubungi Admin hanya muncul jika tidak ada nomor
            markup.add(InlineKeyboardButton("❌ Nomor Hilang", callback_data=f"hubungi_admin_{user_id}"))
        else:
            teks = "📂 Nomor Anda:\n\n" + "\n".join([f"📞 {nomor}" for nomor in nomor_data])
            markup = InlineKeyboardMarkup()

            # Tombol Minta OTP jika nomor ada
            markup.add(InlineKeyboardButton("📩 Minta OTP", callback_data=f"minta_otp_{user_id}"))

        # Tombol Kembali selalu ada
        markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="beli_nomor"))

        bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Terjadi kesalahan: {e}")


# ------------------ HUBUNGI ADMIN ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("hubungi_admin_"))
def hubungi_admin(call):
    user_id = str(call.from_user.id)  # Ambil user ID dari pembeli yang menghubungi admin

    try:
        # Kirim pesan konfirmasi ke pembeli
        bot.send_message(call.message.chat.id, "📩 Permintaan Anda sudah diterima, mohon menunggu respon dari admin.")

        # Hapus daftar nomor dan tombol yang ada sebelumnya
        bot.edit_message_text("📩 Permintaan Anda sudah diterima, mohon menunggu respon dari admin.", 
                              call.message.chat.id, call.message.message_id)

        # Kirim notifikasi ke admin dengan informasi pembeli tanpa nomor yang dibeli
        teks_admin = f"📞 Pembelian nomor oleh pengguna\n\n" \
                     f"Nama: {call.from_user.first_name} {call.from_user.last_name}\n" \
                     f"Username: @{call.from_user.username}\n" \
                     f"ID Telegram: {call.from_user.id}\n"

        markup_admin = InlineKeyboardMarkup()
        # Tombol Hubungi Pembeli yang membuka chat langsung dengan user
        markup_admin.add(InlineKeyboardButton("📩 Hubungi Pembeli", url=f"tg://user?id={user_id}"))
        markup_admin.add(InlineKeyboardButton("✅ Selesai", callback_data=f"selesai_{user_id}"))

        # Kirim pesan notifikasi ke admin tanpa informasi nomor
        bot.send_message(ADMIN_ID, teks_admin, reply_markup=markup_admin)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Terjadi kesalahan: {str(e)}")
        
# ------------------ TOMBOL SELESAI ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("selesai_"))
def selesai(call):
    user_id = call.data.split("_")[1]  # Ambil user ID dari tombol selesai
    try:
        # Mengirim konfirmasi ke admin bahwa proses telah selesai
        bot.send_message(call.message.chat.id, "✅ Proses selesai. Transaksi telah diselesaikan.")

        # Hapus pesan yang sebelumnya ada di admin (notifikasi transaksi)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Terjadi kesalahan: {str(e)}")
        
# ------------------ PILIH NOMOR UNTUK OTP ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("minta_otp_"))
def pilih_nomor_otp(call):
    user_id = str(call.from_user.id)  # Ambil user ID dari pengguna yang meminta OTP

    try:
        with open("user_data.json", "r") as file:
            data = json.load(file)

        nomor_list = data.get(user_id, [])
        if not nomor_list:
            bot.answer_callback_query(call.id, "❌ Anda belum memiliki nomor yang bisa diminta OTP.", show_alert=True)
            return

        # Hanya tampilkan nomor luar negeri yang bukan nomor Indonesia (+62)
        nomor_luar_negeri = [nomor for nomor in nomor_list if not nomor.startswith("+62")]  # +62 adalah kode negara Indonesia

        if not nomor_luar_negeri:
            bot.answer_callback_query(call.id, "❌ Anda tidak memiliki nomor luar negeri yang bisa digunakan untuk OTP.", show_alert=True)
            return

        # Buat markup dengan daftar nomor
        markup = InlineKeyboardMarkup()
        for nomor in nomor_luar_negeri:
            markup.add(InlineKeyboardButton(f"📞 {nomor}", callback_data=f"otp_{user_id}_{nomor}"))

        # Tambahkan tombol kembali ke dalam markup yang sama
        markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="nomor_saya"))

        # Kirim pesan dengan pilihan nomor + tombol kembali
        bot.edit_message_text("📩 Pilih nomor untuk OTP:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Terjadi kesalahan. Coba lagi nanti.", show_alert=True)

# ------------------ KIRIM PERMINTAAN OTP KE ADMIN ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("otp_"))
def kirim_permintaan_otp(call):
    _, user_id, nomor = call.data.split("_")

    # Cek jika nomor Indonesia, tampilkan pesan peringatan
    if nomor.startswith("+62"):
        bot.answer_callback_query(call.id, "❌ Nomor Indonesia tidak bisa digunakan untuk menerima OTP.", show_alert=True)
        return

    teks_admin = f"🔔 Permintaan OTP Baru!\n👤 Pembeli: `{user_id}`\n📞 Nomor: `{nomor}`"
    markup_admin = InlineKeyboardMarkup()
    markup_admin.add(InlineKeyboardButton("📩 Hubungi Pembeli", url=f"tg://user?id={user_id}"))
    markup_admin.add(InlineKeyboardButton("✅ Selesai", callback_data=f"selesai_{call.message.message_id}"))

    # Kirim pesan ke admin
    bot.send_message(ADMIN_ID, teks_admin, parse_mode="Markdown", reply_markup=markup_admin)

    bot.edit_message_text("✅ Permintaan OTP telah dikirim ke admin.", call.message.chat.id, call.message.message_id)

# ------------------ ADMIN SELESAIKAN PERMINTAAN OTP ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("selesai_"))
def selesai_otp(call):
    try:
        message_id = int(call.message.message_id)  # ID pesan yang dikirim ke admin

        # Hapus pesan dari chat admin
        bot.delete_message(call.message.chat.id, message_id)

        # Beri respon ke admin agar tidak muncul error pop-up
        bot.answer_callback_query(call.id, "✅ Permintaan OTP telah diselesaikan.", show_alert=False)

    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Gagal menghapus pesan. Mungkin sudah dihapus.", show_alert=True)
        
# Fungsi-fungsi lainnya di sini...

@bot.callback_query_handler(func=lambda call: call.data == "info")
def informasi(call):
    teks = """📌 Ketentuan & Cara Pakai  

🔹 Ketentuan:  
1️⃣ No Refund. Setelah membeli nomor, nomor tidak bisa diganti atau dikembalikan, kecuali ada masalah pada nomor yang diberikan.  
2️⃣ Kami tidak bertanggung jawab atas pemblokiran nomor yang digunakan untuk kegiatan ilegal atau dilarang.  
3️⃣ Nomor yang sudah dibeli hanya untuk penggunaan pribadi dan tidak dijual ulang.  

🔧 Cara Pakai Bot:  
1️⃣ Ketika kamu siap membeli nomor, pilih layanan melalui menu Beli Nomor.  
2️⃣ Pilih metode pembayaran yang tersedia (QRIS, DANA, GoPay).  
3️⃣ Setelah pembayaran dikonfirmasi oleh admin, nomor akan dikirimkan langsung ke kamu.  
4️⃣ Nomor hanya bisa digunakan untuk verifikasi Telegram.  
5️⃣ Jika kamu ingin meminta OTP untuk nomor yang sudah dibeli, kamu bisa menggunakan tombol Minta OTP pada menu Nomor Saya.  

⚠️ Harap jangan terminate session yang bernama "PC 64bit loginacc 1.30.0" atau terminate all other sessions, agar Anda tetap bisa menerima OTP."""

    markup = InlineKeyboardMarkup()  
    # Tombol Kembali ke Home
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="home"))  # Tombol Home

    # Menghapus pesan sebelumnya dan mengirim pesan baru
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "baca_")
def baca_(call):
    teks = """⚠️ PERINGATAN ⚠️\n\nHANYA NOMOR LUAR YG BISA MEMINTA KEMBALI OTP DI BOT DENGAN SYARAT JANGAN TERMINATE SESSION YG BERNAMA "PC 64BIT".\n\nJIKA SESSION TERSEBUT TERMINATE ( SENGAJA MAUPUN TIDAK ),ADMIN TIDAK BERTANGGUNGJAWAB. \n\nSECARA OTOMATIS, NOMOR TERSEBUT TIDAK BISA LAGI MEMINTA OTP DI BOT INI!"""

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Kembali", callback_data="proses_beli"))
    
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    # ------------------ TOMBOL HOME ------------------
@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    # Menghapus pesan sebelumnya
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Kirim pesan utama setelah tombol home ditekan
    save_user_state(call.from_user.id, "start")
    start(call.message)
        
bot.infinity_polling()