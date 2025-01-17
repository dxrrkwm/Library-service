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

            return borrowing

    @staticmethod
    def _params_to_ints(params):
        try:
            return [int(str_id) for str_id in params.split(",")]
        except ValueError:
            raise ValidationError({"error": "Invalid user ID format. Expected a comma-separated list of integers."})

    def get_queryset(self):
        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)

        if is_active:
            activ_validate_list = ["true", "True", "false", "False"]

            if is_active in activ_validate_list:
                queryset = queryset.filter(user__is_active=is_active)
            else:
                raise ValidationError({"is_active": "Invalid value. Use true, True, or false, False."})

        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        return queryset.select_related("book", "user").prefetch_related("payments").distinct()

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
                type={"type": "bool", "items": {"type": "bool"}},
                description="Filter by user's active status "
                            "(ex. ?is_activ=True(true) or False(false))",
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

        if "actual_return_date" in request.data:
            raise ValidationError({"error": "You cannot update actual_return_date."})

        if "borrow_date" in request.data:
            raise ValidationError({"error": "You cannot update borrow_date."})

        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ReturnBookView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            borrowing = Borrowing.objects.get(pk=pk)
        except Borrowing.DoesNotExist:
            return Response(
                {"error": "Borrowing not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if borrowing.actual_return_date:
            raise ValidationError({"error": "The book has already been returned."})

        with transaction.atomic():
            borrowing.actual_return_date = now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

        create_stripe_session(borrowing, request)

        return Response(
            {"message": "The book has been successfully returned."},
            status=status.HTTP_200_OK
        )
