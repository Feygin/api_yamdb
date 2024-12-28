from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .constants import USERNAME_REGEX


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации нового пользователя.
    Запрашиваемые поля: email, username.
    Если пользователь уже существует с указанным username, проверяем email.
    Генерируем код подтверждения и отправляем на почту.
    """
    email = serializers.EmailField(
        required=True,
        max_length=254,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.'
        }
    )
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        required=True,
        error_messages={
            'invalid': (
                'username содержит недопустимые символы. '
                'Допустимы только буквы, цифры и символы @.+-_'
            ),
            'max_length': 'Длина username не должна превышать 150 символов.'
        }
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError(
                'Использование "me" в качестве username запрещено.'
            )
        return value

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']

        user_with_same_email = User.objects.filter(email=email).first()
        user_with_same_username = User.objects.filter(username=username).first()

        errors = {}

        if user_with_same_username and user_with_same_username.email != email:
            errors['username'] = ['Username уже существует с другим email.']

        if user_with_same_email and user_with_same_email.username != username:
            errors['email'] = ['Email уже зарегистрирован другим пользователем.']

        if errors:
            raise ValidationError(errors)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created and user.email != email:
            errors['username'] = ['Username уже существует с другим email.']
            raise ValidationError(errors)

        user.set_new_confirmation_code()

        send_mail(
            subject='Подтверждение почты',
            message=f'Ваш код подтвeрждeния почты: {user.confirmation_code}',
            from_email='mail@yamdb.ru',
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
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и редактирования пользователей администратором.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )


class MeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и обновления данных своей учётной записи.
    Роль и username нельзя менять.
    """
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        required=False,
        error_messages={
            'invalid': (
                'username содержит недопустимые символы. '
                'Допустимы только буквы, цифры и символы @.+-_'
            ),
            'max_length': 'Длина username не должна превышать 150 символов.'
        }
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использование "me" в качестве username запрещено.'
            )
        return value

    def update(self, instance, validated_data):
        """
        Поле username при PATCH должно валидироваться, но фактически
        не меняться. Если пользователь передал другой username, либо ругаемся,
        либо игнорируем.
        """
        new_username = validated_data.get('username')
        current_username = instance.username

        if new_username is not None and new_username != current_username:
            raise serializers.ValidationError({
                'username': 'Изменение username не разрешено.'
            })

        validated_data.pop('username', None)

        return super().update(instance, validated_data)
