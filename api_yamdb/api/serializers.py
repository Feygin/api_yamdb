from rest_framework import serializers

from reviews.models import Review, Comment


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
            if Review.objects.filter(title_id=title_id, author=author).exists():
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
