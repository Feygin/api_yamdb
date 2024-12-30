from rest_framework import serializers
from reviews.models import Category, Genre, Title


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
        Если описание отсутствует, возвращаем пустую строку."""
        representation = super().to_representation(instance)
        if not representation.get("description"):
            representation["description"] = ""
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
        representation["category"] = CategorySerializer(instance.category).data
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
