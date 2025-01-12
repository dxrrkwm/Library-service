import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books_service.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class TelegramBotTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Hard",
            inventory=5,
            daily_fee=1.50,
        )

    @patch("telegram.signals.bot.send_message")
    def test_actual_borrowings_signal(self, mock_send_message):
        os.environ["TG_ADMIN_CHAT"] = "123456"

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2025-01-10"
        )

        mock_send_message.assert_called_once_with(
            chat_id="123456",
            text=(
                f"user email: {borrowing.user.email} "
                f"book: {borrowing.book} "
                f"return to: {borrowing.expected_return_date}"
            )
        )


    @patch("telegram.signals.bot.send_message")
    def test_closed_payments(self, mock_send_message):
        os.environ["TG_ADMIN_CHAT"] = "123456"

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2025-01-10"
        )

        payment = Payment.objects.create(
            status=Payment.PaymentStatus.PENDING,
            type=Payment.PaymentType.PAYMENT,
            borrowing=borrowing,
            session_url="https://example.com",
            session_id="123456",
            money_to_pay="12.11"
        )

        payment.status = Payment.PaymentStatus.PAID
        payment.save()

        mock_send_message.assert_called_with(
            chat_id="123456",
            text=f"{payment} user email: {payment.borrowing.user.email} Payment closed"
        )

        payment.status = Payment.PaymentStatus.CANCELED
        payment.save()

        mock_send_message.assert_called_with(
            chat_id="123456",
            text=f"Payment Cancelled {payment} user email: {payment.borrowing.user.email}"
        )
