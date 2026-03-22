from os import environ

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackContext, filters
from flask import Flask
import threading

ap = Flask(__name__)
@ap.route('/')
def home():
    return 'Bot is running'
def run_flask():
    port = int(environ.get("PORT", 5000))
    ap.run(host="0.0.0.0", port=port)



BOT_TOKEN = "8444605011:AAE0SKPtijKiSyWn4M1-o1z46dQKj8gb3YA"
CHANNEL_ID = "@theBenhub"
LIMIT = 3
DB_FILE = "user_limits.json"

# So‘kin so‘zlar va behayo so‘zlar ro‘yxati
BAD_WORDS = ["sik", "сик", "dalbayop", "далбайоп", "badword2"]  # haqiqiy so‘zlar bilan to‘ldiring

# Pullik to‘lov variantlari
PAY_OPTIONS = {
    "5k_texts": {"text": "5 000 so‘m → 10 matn", "url": "https://payme.uz/link1"},
    "10k_texts": {"text": "10 000 so‘m → 20 matn", "url": "https://payme.uz/link2"},
    "20k_texts_photos": {"text": "20 000 so‘m → 30 matn + 5 rasm", "url": "https://payme.uz/link3"}
}

# foydalanuvchi limitlarini yuklash
try:
    with open(DB_FILE, "r") as f:
        user_data = json.load(f)
except:
    user_data = {}

async def show_payment_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(option["text"], url=option["url"])]
        for option in PAY_OPTIONS.values()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Sizning bepul limit tugadi. To‘lov variantlarini tanlang:",
        reply_markup=reply_markup
    )

async def forward_with_limit(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    count = user_data.get(user_id, 0)
    msg = update.message

    # Komandalarni yubormaymiz
    if msg.text and msg.text.startswith("/"):
        return

    # So‘kin va behayo so‘zlarni tekshirish
    text_to_check = msg.text.lower() if msg.text else ""
    if any(bad in text_to_check for bad in BAD_WORDS):
        await update.message.reply_text("Bunday xabar qabul qilinmaydi!")
        return

    # Bepul limitni tekshirish
    if count < LIMIT:
        # Birinchi uchtalikda faqat matn bo‘lsin
        if not msg.text:
            await update.message.reply_text("Bepul limitda faqat matn yozishingiz mumkin!")
            return

        # Kanalga yuborish
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg.text)

        user_data[user_id] = count + 1
        with open(DB_FILE, "w") as f:
            json.dump(user_data, f)

        await update.message.reply_text(f"Bepul xabaringiz yuborildi! ({user_data[user_id]}/{LIMIT})")
    else:
        # limit tugagan, pullik menyuni ko‘rsatish
        await show_payment_menu(update, context)

def main():
 try:
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, forward_with_limit))
    print("Bot ishga tushdi...")
    app.run_polling()
 except Exception as exc:
        print('error ',exc)

    

if __name__ == "__main__":
    main()