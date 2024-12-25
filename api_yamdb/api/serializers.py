from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва (Review)."""
    author = serializers.StringRelatedField(
        slig_field='username',
        read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author')
            )
        ]

    def validate_score(self, value):
        """Проверяет, что оценка находится в пределах от 1 до 10."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев (Comment)."""
    author = serializers.StringRelatedField(
        slig_field='username',
        read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')
