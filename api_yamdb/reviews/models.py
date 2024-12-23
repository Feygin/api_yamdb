from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="Genre Name"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        regex=r"^[-a-zA-Z0-9_]+$",
        verbose_name="Slug"
    )

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="Category Name"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        regex=r"^[-a-zA-Z0-9_]+$",
        verbose_name="Slug"
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Title Name"
    )
    year = models.PositiveIntegerField(
        validators=[MaxValueValidator(datetime.now().year)],
        verbose_name="Year of Release",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description"
    )
    genre = models.ManyToManyField(
        "Genre",
        related_name="titles",
        verbose_name="Genres"
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Category",
    )

    @property
    def rating(self):
        return (
            self.reviews.aggregate(models.Avg("score"))
            .get("score__avg")
        )

    class Meta:
        verbose_name = "Title"
        verbose_name_plural = "Titles"

    def __str__(self):
        return self.name
