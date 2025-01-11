from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


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
    rating = serializers.IntegerField(read_only=True)

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
    rating = serializers.IntegerField(read_only=True)

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
