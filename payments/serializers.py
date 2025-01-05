from rest_framework import serializers

from borrowings.serializers import BorrowingDetailSerializer, BorrowingSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )
        read_only_fields = ("id",)


class PaymentListSerializer(PaymentSerializer):
    borrowing = BorrowingSerializer(read_only=True)


class PaymentDetailSerializer(PaymentSerializer):
    borrowing = BorrowingDetailSerializer(read_only=True)
