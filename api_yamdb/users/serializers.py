from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .constants import USERNAME_REGEX


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации нового пользователя."""
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
        """Проверка username на соответствие установленным правилам."""
        if value.lower() == 'me':
            raise ValidationError(
                {
                    'username': [
                        'Использование "me" в качестве username запрещено.'
                    ]
                }
            )
        return value

    def create(self, validated_data):
        """Создание нового пользователя или обновление существующего."""
        email = validated_data['email']
        username = validated_data['username']

        user_with_same_email = User.objects.filter(email=email).first()
        user_with_same_username = User.objects.filter(
            username=username
        ).first()

        errors = {}

        if user_with_same_username and user_with_same_username.email != email:
            errors['username'] = [
                'Username уже существует с другим email.'
            ]

        if user_with_same_email and user_with_same_email.username != username:
            errors['email'] = [
                'Email уже зарегистрирован другим пользователем.'
            ]

        if errors:
            raise ValidationError(errors)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created and user.email != email:
            raise ValidationError({
                'username': [
                    'Username уже существует с другим email.'
                ]
            })

        user.set_new_confirmation_code()

        send_mail(
            subject='Подтверждение почты',
            message=f'Ваш код подтвeрждeния почты: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""
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
            raise ValidationError(['Неверный код подтверждения.'])

        refresh = RefreshToken.for_user(user)
        return {'token': str(refresh.access_token)}


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения и обновления данных пользователя."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )
        read_only_fields = ('role', 'username')


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для управления пользователями администраторами."""
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        required=True,
        allow_blank=False,
        error_messages={
            'invalid': (
                'username содержит недопустимые символы. '
                'Допустимы только буквы, цифры и символы @.+-_'
            ),
            'max_length': 'Длина username не должна превышать 150 символов.',
            'blank': 'username не может быть пустым.'
        }
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        allow_blank=False,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.',
            'blank': 'email не может быть пустым.'
        }
    )

    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина first_name не должна превышать 150 символов.'
        }
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина last_name не должна превышать 150 символов.'
        }
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError({
                'username': [
                    'Использование "me" в качестве username запрещено.'
                ]
            })
        return value

    def validate(self, data):
        instance = self.instance
        username = data.get('username', getattr(instance, 'username', None))
        email = data.get('email', getattr(instance, 'email', None))

        username_conflict = (
            User.objects.filter(username=username)
            .exclude(pk=getattr(instance, 'pk', None))
            .exists()
        )
        if username_conflict:
            raise ValidationError({
                'username': ['Username уже существует.']
            })

        if email == '':
            raise ValidationError({
                'email': ['email не может быть пустым.']
            })
        email_conflict = (
            User.objects.filter(email=email)
            .exclude(pk=getattr(instance, 'pk', None))
            .exists()
        )
        if email_conflict:
            raise ValidationError({
                'email': ['Email уже зарегистрирован другим пользователем.']
            })

        return data

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор для управления данными своей учётной записи."""
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=150,
        required=False,
        allow_blank=False,
        error_messages={
            'invalid': (
                'username содержит недопустимые символы. '
                'Допустимы только буквы, цифры и символы @.+-_'
            ),
            'max_length': 'Длина username не должна превышать 150 символов.',
            'blank': 'username не может быть пустым.'
        }
    )
    email = serializers.EmailField(
        max_length=254,
        required=False,
        allow_blank=False,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.',
            'blank': 'email не может быть пустым.'
        }
    )
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина first_name не должна превышать 150 символов.'
        }
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина last_name не должна превышать 150 символов.'
        }
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )
        read_only_fields = ('role',)

    def validate(self, data):
        """Проверка данных учётной записи на допустимость и уникальность."""
        instance = self.instance
        new_username = data.get('username', instance.username)
        new_email = data.get('email', instance.email)

        if new_username.lower() == 'me':
            raise ValidationError({
                'username': [
                    'Использование "me" в качестве username запрещено.'
                ]
            })

        username_conflict = (
            User.objects.filter(username=new_username)
            .exclude(pk=instance.pk)
            .exists()
        )
        if username_conflict:
            raise ValidationError({
                'username': ['Username уже существует.']
            })

        if new_email == '':
            raise ValidationError({
                'email': ['email не может быть пустым.']
            })

        email_conflict = (
            User.objects.filter(email=new_email)
            .exclude(pk=instance.pk)
            .exists()
        )
        if email_conflict:
            raise ValidationError({
                'email': ['Email уже зарегистрирован другим пользователем.']
            })

        return data

    def update(self, instance, validated_data):
        """Обновление данных учётной записи после проверки."""
        return super().update(instance, validated_data)
