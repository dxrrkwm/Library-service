import stripe
from django.contrib.auth import settings

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing):
    days_to_borrow = (
            borrowing.expected_return_date - borrowing.borrow_date
    ).days

    total_amount = borrowing.book.daily_fee * days_to_borrow

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
        success_url="http://localhost:8000/api/payments/",
        cancel_url="http://localhost:8000/api/payments/",
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_amount,
    )

    return payment
