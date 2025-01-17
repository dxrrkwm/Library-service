from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse

from payments.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


FINE_MULTIPLIER = 2


def calculate_fine_for_borrowing(borrowing, fine_multiplier=FINE_MULTIPLIER):
    """
    Calculates the fine amount for a borrowing.
    """
    if borrowing.actual_return_date and borrowing.actual_return_date > borrowing.expected_return_date:
        overdue_days = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        fine_amount = Decimal(overdue_days * borrowing.book.daily_fee * fine_multiplier)
        return fine_amount
    return (borrowing.expected_return_date - borrowing.borrow_date).days * borrowing.book.daily_fee


def handle_stripe_error(e):
    """
    Handles Stripe API errors and returns appropriate HTTP responses.
    """
    if isinstance(e, stripe.error.PermissionError):
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
    elif isinstance(e, stripe.error.APIConnectionError):
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    elif isinstance(e, stripe.error.APIError):
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    elif isinstance(e, stripe.error.CardError):
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {"error": str(e)},
        status=status.HTTP_400_BAD_REQUEST
    )


def create_stripe_session(borrowing, request):
    """
    Creates a Stripe session for a borrowing.
    """
    total_amount = calculate_fine_for_borrowing(borrowing)

    success_url = request.build_absolute_uri(
        reverse("payments:payments-success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("payments:payments-cancel")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    try:
        with transaction.atomic():
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": borrowing.book.title,
                            },
                            "unit_amount": int(total_amount) * 100,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url
            )

            payment = Payment.objects.create(
                borrowing=borrowing,
                session_url=session.url,
                session_id=session.id,
                money_to_pay=total_amount
            )

    except stripe.error.StripeError as e:
        return handle_stripe_error(e)

    return payment
