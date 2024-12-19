from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации нового пользователя.
    Запрашиваемые поля: email, username.
    Если пользователь уже существует с указанным username, проверяем email.
    Генерируем код подтверждения и отправляем на почту.
    """
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, max_length=150)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError(
                'Использование "me" в качестве username запрещено.'
            )
        return value

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )
        if not created and user.email != validated_data['email']:
            raise ValidationError('Username уже существует с другим email.')

        user.set_new_confirmation_code()

        send_mail(
            subject='Подтверждение почты',
            message=f'Ваш код подтвeрждeния почты: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения JWT-токена.
    Запрашиваемые поля: username, confirmation_code.
    Проверяем валидность кода и выдаём токен.
    """
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data['username']
        code = data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound('Пользователь не найден.')

        if user.confirmation_code != code:
            raise ValidationError('Неверный код подтверждения.')

        refresh = RefreshToken.for_user(user)
        return {'token': str(refresh.access_token)}


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и частичного обновления данных пользователя.
    Поля role, username для пользователя не редактируемы.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и редактирования пользователей администратором.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')


class MeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и обновления данных своей учётной записи.
    Роль и username нельзя менять.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role', 'username')
