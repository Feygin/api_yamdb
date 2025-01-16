from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title
from api.constants import (USERNAME_REGEX, MAX_LENGTH_USERNAME,
                           MAX_LENGTH_FIRST_NAME, MAX_LENGTH_LAST_NAME,
                           MAX_LENGTH_EMAIL)
from users.models import User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ["id", "name", "year", "rating",
                  "description", "genre", "category"]

    def to_representation(self, instance):
        """Модифицируем данные возвращаемые API.
        Если описание отсутствует, возвращаем пустую строку.
        Если категория отсутствует, возвращаем пустой объект
        категории."""
        representation = super().to_representation(instance)
        if not representation.get("description"):
            representation["description"] = ""
        if not representation.get("rating"):
            representation["rating"] = None
        if instance.category is None:
            representation["category"] = CategorySerializer(None).data
        return representation


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True,
        help_text="Жанр отсутствует в БД.",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
        help_text="Категория отсутствует в БД.",
    )
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ["id", "name", "year", "description",
                  "genre", "category", "rating"]

    def validate_genre(self, value):
        """Проверяем, что наличие данных жанра."""
        if not value:
            raise serializers.ValidationError(
                "The genre field cannot be empty.")
        return value

    def to_representation(self, instance):
        """Модифицируем данные возвращаемые API.
        Если описание отсутствует, возвращаем пустую строку.
        Заменяем слаги на полные данные для жанра и категории."""
        representation = super().to_representation(instance)
        if not representation.get("description"):
            representation["description"] = ""
        if not representation.get("rating"):
            representation["rating"] = None
        representation["genre"] = GenreSerializer(
            instance.genre.all(), many=True).data
        representation["category"] = (
            CategorySerializer(instance.category).data
            if instance.category else CategorySerializer(None).data
        )
        return representation

    def create(self, validated_data):
        """Создаем произведение с жанрами и категорией."""
        genres = validated_data.pop("genre", [])
        category = validated_data.pop("category", None)

        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        title.category = category
        title.save()

        return title

    def update(self, instance, validated_data):
        """Обновляем произведение с жанрами и категорией."""
        genres = validated_data.pop("genre", [])
        category = validated_data.pop("category", None)
        # Обновляем заполненные поля произведения
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.genre.set(genres)
        instance.category = category
        instance.save()

        return instance


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва (Review)."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяет уникальность отзыва от автора для произведения."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        author = request.user

        if request.method == 'POST':
            if Review.objects.filter(
                    title_id=title_id, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data

    def validate_score(self, value):
        """Проверяет, что оценка находится в пределах от 1 до 10."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев (Comment)."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации нового пользователя.
    Запрашиваемые поля: email, username.
    Если пользователь уже существует с указанным username, проверяем email.
    Генерируем код подтверждения и отправляем на почту.
    """
    email = serializers.EmailField(
        required=True,
        max_length=MAX_LENGTH_EMAIL,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.'
        }
    )
    username = serializers.RegexField(
        regex=USERNAME_REGEX,
        max_length=MAX_LENGTH_USERNAME,
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
        max_length=MAX_LENGTH_USERNAME,
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
        max_length=MAX_LENGTH_EMAIL,
        required=True,
        allow_blank=False,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.',
            'blank': 'email не может быть пустым.'
        }
    )

    first_name = serializers.CharField(
        max_length=MAX_LENGTH_FIRST_NAME, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина first_name не должна превышать 150 символов.'
        }
    )
    last_name = serializers.CharField(
        max_length=MAX_LENGTH_LAST_NAME, required=False, allow_blank=True,
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
        max_length=MAX_LENGTH_USERNAME,
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
        max_length=MAX_LENGTH_EMAIL,
        required=False,
        allow_blank=False,
        error_messages={
            'max_length': 'Длина email не должна превышать 254 символов.',
            'blank': 'email не может быть пустым.'
        }
    )
    first_name = serializers.CharField(
        max_length=MAX_LENGTH_FIRST_NAME, required=False, allow_blank=True,
        error_messages={
            'max_length': 'Длина first_name не должна превышать 150 символов.'
        }
    )
    last_name = serializers.CharField(
        max_length=MAX_LENGTH_LAST_NAME, required=False, allow_blank=True,
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
