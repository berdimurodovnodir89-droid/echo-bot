import os
import requests
import urllib3
from dotenv import load_dotenv
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


def get_live_rate():
    """Markaziy bank API-dan real kursni xavfsiz olish funksiyasi"""
    try:
        url = "https://cbu.uz"
        response = requests.get(url, timeout=10, verify=False)
        
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                for item in data:
                    if item['Ccy'] == 'USD':
                        return float(item['Rate'])
            except ValueError:
                print("API'dan noto'g'ri (bo'sh) javob keldi, JSON ga o'tmadi.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Tarmoq xatosi: {e}")
        return None

def start(update: Update, context: CallbackContext):
    text = ("Assalomu alaykum, jigar! Botga xush kelibsiz.\n\n"
            "Buyruqlar:\n"
            "1. /convert [miqdor] - Valyuta kursini hisoblash\n"
            "2. /randomcat - Mushuk rasmi\n"
            "3. /greet [ism] - Salomlashish")
    update.message.reply_text(text)

def randomcat(update: Update, context: CallbackContext):
    update.message.reply_photo(photo='https://cataas.com', caption="Mana jigar, mushuk!")

def greet(update: Update, context: CallbackContext):
   
    msg_parts = update.message.text.split(' ', 1)
    if len(msg_parts) > 1:
        name = msg_parts
        update.message.reply_text(f"Salom {name}, ishlariz yaxshimi?")
    else:
        update.message.reply_text("Ismingizni yozing. Masalan: /greet Ali")

def convert(update: Update, context: CallbackContext):
    current_rate = get_live_rate()
    
    if current_rate is None:
        update.message.reply_text("Hozirda kursni olib bo'lmadi. Zaxira kursi (12850) bilan hisoblayman.")
        current_rate = 12850.0

    try:

        raw_text = update.message.text.lower().replace('/convert', '').replace('usd', '').strip()
        
        if not raw_text:
            update.message.reply_text("Miqdorni yozing. Masalan: /convert 100")
            return

        amount = float(raw_text)
        
        to_uzs = amount * current_rate
        to_usd = amount / current_rate

        javob = (f" Bugungi kurs: 1 $ = {current_rate} so'm\n\n"
                 f"🇺🇸 {amount:,.2f} $  {to_uzs:,.2f} so'm\n"
                 f"🇺🇿 {amount:,.2f} so'm  {to_usd:,.4f} $")
        update.message.reply_text(javob)
    except ValueError:
        update.message.reply_text("Iltimos, faqat son kiriting! Masalan: /convert 50")


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f"Siz dedingiz: {update.message.text}")



def main() -> None:
    token = os.getenv('TOKEN')
    if not token:
        print("XATO: .env faylida TOKEN topilmadi!")
        return

    updater = Updater(token)
    dispatcher = updater.dispatcher


    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('randomcat', randomcat))
    dispatcher.add_handler(CommandHandler('greet', greet))
    dispatcher.add_handler(CommandHandler('convert', convert)) 

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    print("Bot ishga tushdi...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()