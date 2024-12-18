from rest_framework import serializers
from django.core.mail import send_mail
from .models import User, generate_confirmation_code
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound, ValidationError


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, max_length=150)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError("Использование 'me' в качестве username запрещено.")
        return value

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )
        # Если пользователь существует, проверяем email
        if not created and user.email != validated_data['email']:
            raise ValidationError("Пользователь с таким username уже существует с другим email.")

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
        username = data['username']
        code = data['confirmation_code']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден.")

        if user.confirmation_code != code:
            raise ValidationError("Неверный код подтверждения.")

        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('role', 'username')
