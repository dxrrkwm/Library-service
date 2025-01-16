import pytest
from decimal import Decimal
from rest_framework.test import APIClient

from payments.models import Payment
from payments.utils import calculate_fine_for_borrowing, create_stripe_session
from payments.serializers import PaymentSerializer, PaymentListSerializer
from django.urls import reverse, resolve
from payments.views import PaymentListRetrieveViewSet


##models
@pytest.mark.django_db
def test_payment_str_representation(payment_factory):
    payment = payment_factory()
    assert str(payment) == f"{payment.type} for {payment.borrowing.book.title}"


@pytest.mark.django_db
def test_payment_min_money_validation(payment_factory):
    with pytest.raises(ValueError):
        payment_factory(money_to_pay=Decimal("-1.00"))

##serializer
@pytest.mark.django_db
def test_payment_serializer_serialization(payment_factory):
    payment = payment_factory()
    serializer = PaymentSerializer(instance=payment)
    assert serializer.data["id"] == payment.id
    assert serializer.data["status"] == payment.status


@pytest.mark.django_db
def test_payment_list_serializer(payment_factory):
    payment = payment_factory()
    serializer = PaymentListSerializer(instance=payment)
    assert serializer.data["borrowing"]["id"] == payment.borrowing.id

#views
@pytest.mark.django_db
def test_payment_list_view(user_factory, payment_factory):
    user = user_factory()
    client = APIClient()
    client.force_authenticate(user=user)
    payment_factory.create_batch(3, borrowing__user=user)

    response = client.get("/api/payments/")
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_success_view(payment_factory, mocker):
    payment = payment_factory(session_id="test_session")
    mocker.patch("stripe.checkout.Session.retrieve", return_value={"payment_status": "paid"})
    client = APIClient()

    response = client.get(f"/api/payments/success/?session_id={payment.session_id}")
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == Payment.PaymentStatus.PAID


@pytest.mark.django_db
def test_cancel_view(payment_factory):
    payment = payment_factory(status="PENDING")
    client = APIClient()
    response = client.get(f"/api/payments/cancel/?session_id={payment.session_id}")
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == Payment.PaymentStatus.CANCELED

##utils

@pytest.mark.django_db
def test_calculate_fine_for_borrowing_no_overdue(borrowing_factory):
    borrowing = borrowing_factory(expected_return_date="2025-01-10", actual_return_date="2025-01-09")
    fine = calculate_fine_for_borrowing(borrowing)
    expected_fine = Decimal(
        (borrowing.expected_return_date - borrowing.borrow_date).days * borrowing.book.daily_fee
    )
    assert fine == expected_fine


@pytest.mark.django_db
def test_calculate_fine_for_borrowing_with_overdue(borrowing_factory):
    borrowing = borrowing_factory(expected_return_date="2025-01-10", actual_return_date="2025-01-12")
    fine = calculate_fine_for_borrowing(borrowing)
    overdue_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
    expected_fine = Decimal(overdue_days * borrowing.book.daily_fee * 2)
    assert fine == expected_fine


@pytest.mark.django_db
def test_create_stripe_session(mocker, borrowing_factory):
    mocker.patch("stripe.checkout.Session.create", return_value={"id": "test_id", "url": "http://test-url"})
    borrowing = borrowing_factory()
    payment = create_stripe_session(borrowing, mocker.MagicMock())
    assert payment.session_id == "test_id"
    assert payment.session_url == "http://test-url"


##urls
def test_payment_urls():
    url = reverse("payments-list")
    assert resolve(url).func.cls == PaymentListRetrieveViewSet

