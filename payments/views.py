import stripe
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentSerializer,
)
from payments.utils import create_stripe_session, handle_stripe_error


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
        return self.action_serializer_classes.get(
            self.action,
            PaymentSerializer
        )

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "borrowing__book",
            "borrowing__user"
        )

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        url_name="success"
    )
    def success(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID is missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return handle_stripe_error(e)

        if session.payment_status == "paid":
            payment.status = Payment.PaymentStatus.PAID
            payment.save()
            return Response(
                {
                    "message": "Payment was successful",
                    "payment": payment.id,
                    "payment_status": payment.status
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Payment was not successful"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=["GET"],
        detail=False,
        url_path="cancel",
        url_name="cancel"
    )
    def cancel(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID is missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        if payment.status == Payment.PaymentStatus.CANCELED:
            return Response(
                {"error": "Payment was already canceled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow_date = payment.borrowing.borrow_date

        if timezone.now().date() - borrow_date > timezone.timedelta(hours=24):
            return Response(
                {"error": "Session expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = Payment.PaymentStatus.CANCELED
        payment.save()

        create_stripe_session(payment.borrowing, request)

        return Response(
            {
                "message": "Payment was canceled",
                "payment": payment.id,
                "payment_status": payment.status
            },
            status=status.HTTP_200_OK
        )
