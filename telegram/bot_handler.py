import os
from datetime import datetime
from time import sleep

from django.conf import settings
from telebot import TeleBot, types

from borrowings.models import Borrowing

bot = TeleBot(settings.TELEGRAM_BOT_API_KEY)
if os.environ.get("DEBUG"):
    bot.set_webhook(url=f"https://{os.environ["NGROK_HOST"]}/api/telegram/")
else:
    # ToDo add prod URL to prod settings
    bot.set_webhook(url="Prod-URL")
sleep(3)

@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    borrow = types.KeyboardButton("Borrowings")
    today_borrow = types.KeyboardButton("Today's Borrowings")
    markup.add(borrow, today_borrow)
    bot.reply_to(message, "Hello world", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Borrowings")
def send_borrowings(message):
    borrowings = Borrowing.objects.filter(actual_return_date=None)
    out = ""
    for borrowing in borrowings:
        string = (
            f"user email: {borrowing.user.email}, "
            f"book: {borrowing.book.title}, "
            f"need to return: {borrowing.expected_return_date}"
        )
        out += string + "\n"

    if out == "":
        bot.reply_to(message, "No borrowings found")
    else:
        bot.reply_to(message, out)

@bot.message_handler(func=lambda message: message.text == "Today's Borrowings")
def send_borrowings_today(message):
    borrowings = Borrowing.objects.filter(
        actual_return_date=None,
        expected_return_date__lte=datetime.now().date()
    )
    out = ""
    for borrowing in borrowings:
        string = (
            f"user email: {borrowing.user.email}, "
            f"book: {borrowing.book.title}, "
            f"need to return: {borrowing.expected_return_date}"
        )
        out += string + "\n"

    if out == "":
        bot.reply_to(message, "No borrowings found")
    else:
        bot.reply_to(message, out)
