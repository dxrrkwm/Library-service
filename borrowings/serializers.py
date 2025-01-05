from datetime import date

from rest_framework import serializers

from books_service.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.models import Payment
from users.serializers import UserSerializer


class ShortInfoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type"
        )
        read_only_fields = fields


class DetailInfoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay",
            "session_url"
        )
        read_only_fields = fields


class BorrowingSerializer(serializers.ModelSerializer):
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
        read_only_fields = ("id", "actual_return_date")

    def validate_expected_return_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("The expected return date cannot be in the past.")
        return value


class BorrowingListSerializer(BorrowingSerializer):
    user_email = serializers.SlugRelatedField(
        source="user",
        slug_field="email",
        read_only=True
    )
    book_title = serializers.SlugRelatedField(
        source="book",
        slug_field="title",
        read_only=True
    )
    payments = ShortInfoPaymentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "book_title",
            "user_email",
            "actual_return_date",
            "payments"
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    payments = DetailInfoPaymentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments"
        )
