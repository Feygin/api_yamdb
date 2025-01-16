from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from api.filters import TitleFilter
from api.paginations import ReviewPagination
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAuthorAdminModerOrReadOnly)
from api.serializers import (AdminUserSerializer, CategorySerializer,
                             CommentSerializer, GenreSerializer, MeSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleReadSerializer, TitleWriteSerializer,
                             TokenSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
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
    queryset = Title.objects.prefetch_related("genre", "category").annotate(
        rating=Avg("reviews__score")
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ReviewPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

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
    http_method_names = ['get', 'post', 'patch', 'delete']

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


class SignUpView(generics.CreateAPIView):
    """
    Представление для регистрации пользователя.
    При POST-запросе с email и username отправляет код подтверждения.
    """
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, создаёт пользователя, отправляет код."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class TokenObtainView(APIView):
    """
    Представление для получения JWT-токена.
    Принимает username и confirmation_code, возвращает токен.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Обрабатывает POST-запрос и возвращает JWT-токен."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    Доступен только администратору.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT-запросы (Method Not Allowed)."""
        if request.method.upper() == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """PATCH-запрос с валидацией данных."""
        return super().partial_update(request, *args, **kwargs)


class MeView(generics.RetrieveUpdateAPIView):
    """
    Представление для просмотра и изменения своих данных (профиля).
    Доступно только аутентифицированному пользователю.
    """
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Возвращает текущего аутентифицированного пользователя."""
        return self.request.user
