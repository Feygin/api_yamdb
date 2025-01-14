from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAdmin
from api.serializers import (AdminUserSerializer, MeSerializer,
                             SignUpSerializer, TokenSerializer)
from users.models import User


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
