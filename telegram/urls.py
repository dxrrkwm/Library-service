from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from telegram.views import webhook

urlpatterns = [
    path("", csrf_exempt(webhook), name="start-bot"),
]

app_name = "telegram"
