import enum

from django.db import models


class CoverTypes(enum.Enum):
    HARD = "Hard"
    SOFT = "Soft"


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

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"
