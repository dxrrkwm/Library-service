import telebot
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from telegram.bot_handler import bot


@csrf_exempt
def webhook(request):
    print("test")
    if request.method == "POST":
        json_str = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({"ok": True})
    return JsonResponse({"error": "Invalid request"}, status=400)
