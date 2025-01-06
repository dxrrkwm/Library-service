import stripe
from django.conf import settings
from rest_framework.reverse import reverse

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, request):
    days_to_borrow = (
            borrowing.expected_return_date - borrowing.borrow_date
    ).days

    total_amount = borrowing.book.daily_fee * days_to_borrow

    success_url = request.build_absolute_uri(
        reverse("payments:payments-success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("payments:payments-cancel")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

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

    return payment
