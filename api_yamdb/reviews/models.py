from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()


class Genre(models.Model):
    """Модель для жанров."""
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="Жанр"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        regex=r"^[-a-zA-Z0-9_]+$",
        verbose_name="Slug"
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель для категорий."""
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="Категория"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        regex=r"^[-a-zA-Z0-9_]+$",
        verbose_name="Slug"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name="Наименование произведения"
    )
    year = models.PositiveIntegerField(
        validators=[MaxValueValidator(datetime.now().year)],
        verbose_name="Год выпуска",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание"
    )
    genre = models.ManyToManyField(
        "Genre",
        related_name="titles",
        verbose_name="Жанр"
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория",
    )

    @property
    def rating(self):
        return (
            self.reviews.aggregate(models.Avg("score"))
            .get("score__avg")
        )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name
