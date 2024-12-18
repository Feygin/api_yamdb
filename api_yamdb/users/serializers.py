from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import User, generate_confirmation_code
from rest_framework.exceptions import NotFound


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'role')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Использование 'me' в качестве username запрещено.")
        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.confirmation_code = generate_confirmation_code()
        user.save()
        send_mail(
            subject="Your confirmation code",
            message=f"Your confirmation code is {user.confirmation_code}",
            from_email="no-reply@example.com",
            recipient_list=[user.email],
        )
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = User.objects.filter(username=username).first()
        if not user:
            raise NotFound("Пользователь не найден.")

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
