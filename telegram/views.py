import os

import telebot
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from telegram.bot_handler import bot

if os.getenv("DEBUG"):
    ngrok_host = os.getenv("NGROK_HOST")
    if ngrok_host:
        bot.set_webhook(url=f"https://{ngrok_host}/api/telegram/")
    else:
        raise Exception("NGROK_HOST is not set")
else:
    prod_host = os.getenv("PROD_HOST")
    if prod_host:
        bot.set_webhook(url=f"https://{prod_host}/api/telegram/")
    else:
        raise Exception("PROD_HOST is not set")


@csrf_exempt
def webhook(request):
    print("test")
    if request.method == "POST":
        json_str = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({"ok": True})
    return JsonResponse({"error": "Invalid request"}, status=400)
