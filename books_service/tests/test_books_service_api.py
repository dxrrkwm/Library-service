from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books_service.models import Book, CoverTypes

BOOKS_SERVICE_URL = reverse("books_service:book-list")


def fixture_book_data():
    return {
        "title": "Book",
        "author": "Author",
        "cover": CoverTypes.HARD.value,
        "inventory": 10,
        "daily_fee": 3.00
    }


def sample_book(**params):
    defaults = {
        "title": "Book",
        "author": "Author",
        "cover": CoverTypes.HARD.value,
        "inventory": 10,
        "daily_fee": 3.00
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBooksServiceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_books(self):
        res = self.client.get(BOOKS_SERVICE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = reverse("books_service:book-detail", args=[book.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedBooksServiceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "password123"
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        payload = fixture_book_data()
        res = self.client.post(BOOKS_SERVICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_forbidden(self):
        book = sample_book()
        url = reverse("books_service:book-detail", args=[book.id])
        payload = fixture_book_data()
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        book = sample_book()
        url = reverse("books_service:book-detail", args=[book.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBooksServiceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "password123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = fixture_book_data()
        res = self.client.post(BOOKS_SERVICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_with_invalid_data(self):
        payload = fixture_book_data()
        payload["title"] = ""
        res = self.client.post(BOOKS_SERVICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
