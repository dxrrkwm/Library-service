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
