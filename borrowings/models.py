from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def calculate_total_price(self):
        if self.actual_return_date:
            days_borrowed = (self.actual_return_date - self.borrow_date).days
        else:
            days_borrowed = (datetime.date.today() - self.borrow_date).days
        return Decimal(days_borrowed) * self.book.daily_fee

    def clean(self):
        if self.borrow_date > datetime.date.today():
            raise ValidationError(
                {"borrow_date": "The borrow date cannot be in the future."}
            )

        if self.expected_return_date <= self.borrow_date:
            raise ValidationError(
                {"expected_return_date": "The expected return date must be after the borrow date."}
            )


        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError(
                {"actual_return_date": "The actual return date cannot be earlier than the borrow date."}
            )


        if self.actual_return_date and self.actual_return_date < self.expected_return_date:
            raise ValidationError(
                {"actual_return_date": "The actual return date cannot be earlier than the expected date."}
            )
