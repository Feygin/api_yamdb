from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from reviews.models import Review, Title
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorAdminModerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]

    def get_title(self):
        """Получает объект произведения."""
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        """Возвращает все отзывы для конкретного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Сохраняет новый отзыв с автором и привязывает его к произведению."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]

    def get_review(self):
        """Получает объект отзыва."""
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        """Возвращает все комментарии для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Сохраняет новый комментарий с автором и привязывает его к отзыву."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
