from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class Review(models.Model):
    title = models.CharField('Произведение', max_length=255)  # временно
    author = models.IntegerField('Автор', null=True, blank=True)  # временно
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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text

    @staticmethod
    def get_average_rating(title_id):
        reviews = Review.objects.filter(title_id=title_id)
        average_score = reviews.aggregate(Avg('score'))['score__avg']
        return round(average_score) if average_score else None


class Comment(models.Model):
    review = models.ForeignKey(
        'Отзыв', Review, on_delete=models.CASCADE, related_name='comments')
    author = models.IntegerField('Автор', null=True, blank=True)  # временно
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
