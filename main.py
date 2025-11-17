import telebot
from flask import Flask
from telebot import types

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello():
    return "Salom bot ishlayapti", 200


# BOT tokeni
TOKEN = "8413767557:AAFslk-Ej9KRX3XgU5vHArRErr348HQkcGs"
bot = telebot.TeleBot(TOKEN)


# Botni kodlari


@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg, "Salom, bot ishlayapti ! ")


# obuna bolish kerak bolgan kanallar
CHANNELS = [
    "@ownclouds", "@kinolar_doramalar_uz", "@AnimeWorldCafe"
]


# User kanallaga obuna bolganmi yoki yoq tekshrsh
def check_user(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked']:
                return False
        except:
            return False
    return True


# databasaga saqlash
from pymongo import MongoClient

MONGO_URL = "mongodb+srv://kinochi.l0u51kz.mongodb.net/"
client = MongoClient(MONGO_URL)

db = client["kinochi_bot"]
collection = db["videos"]


@bot.channel_post_handler(content_types=["video"])
def handle_channel_post(message):
    # OZINGZINI TELEGRAM KANALINGIZNI KIRITING
    if message.chat.username in ["movieworldcafe_mwc", "AnimeWorldCafe", "HentaiWorldCafe"]:
        collection.insert_one({
            "file_id": message.video.file_id,
            "caption": message.caption
        })


# obuna bolmagan bolsa sorov berish
def ask_to_subscribe(chat_id):
    markup = types.InlineKeyboardMarkup()

    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(text=ch, url=f"https://t.me/{ch[1:]}"))

    markup.add(types.InlineKeyboardButton("tekshirish", callback_data="check"))

    bot.send_message(chat_id, "Botdan foydalanish uchun kanallarga obuna boling", reply_markup=markup)


# start bosilganda
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_user(user_id):
        bot.send_message(message.chat.id, "Botdan foydalanishingiz mumkin!")
    else:
        # agar obuna bolmagan bolsa
        ask_to_subscribe(message.chat.id)


# tekshrsh tugmasi bosilganda
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    user_id = call.from_user.id
    if check_user(user_id):
        bot.send_message(call.message.chat.id, "Botdan foydalanishingiz mumkin!")
    else:
        bot.send_message(call.message.chat.id, "Barcha kanallarga obuna bolmagansiz!")


# har qanday habar kelganda tekshrsh
@bot.message_handler(func=lambda message: True)
def all_messages(message):
    user_id = message.from_user.id
    if not check_user(user_id):
        ask_to_subscribe(message.chat.id)
        return

    if message.text.isdigit():
        for video in collection.find():
            if f"Kod: {message.text}" in video["caption"]:
                bot.send_video(
                    message.chat.id,
                    video["file_id"],
                    caption=video["caption"]
                )
    else:
        bot.send_message(message.chat.id, "Noto'g'ri formatdagi kod")


bot.polling()

