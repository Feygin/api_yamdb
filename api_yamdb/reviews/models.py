from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from reviews.constants import TEXT_MAX_LENGTH

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
        """ Cчитает средний рэйтинг произведения. """
        result = self.reviews.aggregate(average=Avg('score'))
        average_score = result['average']
        return int(round(average_score)) if average_score is not None else None

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для отзывов о произведениях."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Произведение"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'

    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, 'Оценка должна быть не меньше 1'),
            MaxValueValidator(10, 'Оценка должна быть не больше 10')
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:TEXT_MAX_LENGTH]


class Comment(models.Model):
    """Модель для комментариев к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:TEXT_MAX_LENGTH]
