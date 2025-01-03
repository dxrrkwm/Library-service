from datetime import date

from rest_framework import serializers

from books_service.serializers import BookSerializer
from users.serializers import UserSerializer

from .models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )

    def validate_expected_return_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("The expected return date cannot be in the past.")
        return value


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
