from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentSerializer,
)


class PaymentListRetrieveViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    permission_classes = [IsAuthenticated]
    action_serializer_classes = {
        "list": PaymentListSerializer,
        "retrieve": PaymentDetailSerializer
    }

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, PaymentSerializer)

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing")

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)
