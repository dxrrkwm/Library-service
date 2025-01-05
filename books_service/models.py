import enum
import os
import uuid

from django.db import models
from django.utils.text import slugify


class CoverTypes(enum.Enum):
    HARD = "Hard"
    SOFT = "Soft"


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=15,
        choices=[(tag.value, tag.name) for tag in CoverTypes],
        default=CoverTypes.HARD.value,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    image = models.ImageField(null=True, upload_to=movie_image_file_path)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"
