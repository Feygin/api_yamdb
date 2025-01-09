from api.filters import TitleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from reviews.models import Category, Genre, Title, Review

from api.paginations import ReviewPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorAdminModerOrReadOnly
from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleReadSerializer, TitleWriteSerializer,
                             ReviewSerializer, CommentSerializer)


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = ReviewPagination
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = ReviewPagination
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related("genre", "category").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter  # Correctly assign the filter set
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ReviewPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TitleReadSerializer
        return TitleWriteSerializer

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT."""
        if request.method == "PUT":
            raise MethodNotAllowed(
                "PUT", detail="PUT method is not allowed for this endpoint."
            )
        return super().update(request, *args, **kwargs)

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

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT-запросы, но разрешаем PATCH-запросы."""
        if request.method == 'PUT':
            raise MethodNotAllowed(
                "PUT", detail="Метод PUT не разрешен."
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]

    def get_review(self):
        """Получает объект отзыва."""
        return get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Возвращает все комментарии для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Сохраняет новый комментарий с автором и привязывает его к отзыву."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT-запросы, но разрешаем PATCH-запросы."""
        if request.method == 'PUT':
            raise MethodNotAllowed(
                "PUT", detail="Метод PUT не разрешен."
            )
        return super().update(request, *args, **kwargs)