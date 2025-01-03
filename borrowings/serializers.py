from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Borrowing
from books_service.serializers import BookSerializer

class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(
        source="book.title", read_only=True
    )
    user = serializers.CharField(
        source="user.email", read_only=True
    )

    class Meta:
        model = Borrowing
        fields = ("id",  "book", "user")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
