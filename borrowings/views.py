import stripe
from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingSerializer,
)
from payments.utils import create_stripe_session


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related(
        "book",
        "user"
    ).prefetch_related("payments")
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        with transaction.atomic():
            book = serializer.validated_data["book"]
            if book.inventory <= 0:
                raise ValidationError({"error": "The book is not available for borrowing."})
            book.inventory -= 1
            book.save()

            borrowing = serializer.save(user=self.request.user)

            create_stripe_session(borrowing, self.request)
            return borrowing

    @staticmethod
    def _params_to_ints(params):
        return [int(str_id) for str_id in params.split(",")]

    def get_queryset(self):
        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)

        if is_active:
            queryset = queryset.filter(user__is_active=is_active)

        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingListSerializer
        return BorrowingSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by user id (ex. ?user=2,5)",
            ),
            OpenApiParameter(
                "is_active",
                type={"type": "bool", "items": {"type": "number"}},
                description="Filter by user is activ "
                            "(ex. ?is_activ=1 or 0)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Borrowing.objects.select_related(
        "book",
        "user"
    ).prefetch_related("payments")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            self.queryset = self.queryset.filter(user=self.request.user)
        return self.queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def update(self, request, *args, **kwargs):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            raise ValidationError({"error": "The book has already been returned."})

        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            current_session = borrowing.payments.filter(status="PENDING").first()
            if current_session:
                try:
                    stripe.checkout.Session.expire(current_session.session_id)
                except stripe.error.StripeError as e:
                    raise ValidationError(
                        {"error": f"Failed to expire the session: {str(e)}"}
                    )

            borrowing.payments.filter(status="PENDING").delete()
            borrowing = serializer.save()

            create_stripe_session(borrowing, request)

        return Response(serializer.data)


class ReturnBookView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            borrowing = Borrowing.objects.get(pk=pk)
        except Borrowing.DoesNotExist as err:
            raise ValidationError({"error": "Borrowing not found."}) from err

        if borrowing.actual_return_date:
            raise ValidationError({"error": "The book has already been returned."})

        with transaction.atomic():
            borrowing.actual_return_date = now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

        return Response(
            {"message": "The book has been successfully returned."},
            status=status.HTTP_200_OK
        )
