import os
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from books_service.models import Book

BOOK_URL = reverse("books_service:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "inventory": 1,
        "daily_fee": 1,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def image_upload_url(book_id):
    return reverse("books_service:book-upload-image", args=[book_id])


def detail_url(book_id):
    return reverse("books_service:book-detail", args=[book_id])


class BookImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@myproject.com", password="password"
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def tearDown(self):
        self.book.image.delete()

    def test_upload_image_to_book(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.book.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_book_list_should_work(self):
        url = BOOK_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "author": "Author",
                    "inventory": 1,
                    "daily_fee": 1,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(title="Title")
        self.assertTrue(book.image)

    def test_image_url_is_shown_on_book_detail(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.book.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_book_list(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(BOOK_URL)

        self.assertIn("image", res.data[0].keys())
