import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowings.models import Borrowing
from payments.models import Payment
from telegram.bot_handler import bot


@receiver([post_save], sender=Borrowing)
def actual_borrowings(sender, instance, **kwargs):
    new_borrowing = instance
    text = (f"user email: {new_borrowing.user.email} "
            f"book: {new_borrowing.book} "
            f"return to: {new_borrowing.expected_return_date}")
    bot.send_message(chat_id=os.environ["TG_ADMIN_CHAT"], text=text)

@receiver(post_save, sender=Payment)
def closed_payments(sender, instance, **kwargs):
    if instance.status == Payment.PaymentStatus.Paid:
        bot.send_message(
            chat_id=os.environ["TG_ADMIN_CHAT"],
            text=f"{instance} user email: {instance.borrowing.user.email} Payment closed"
        )
