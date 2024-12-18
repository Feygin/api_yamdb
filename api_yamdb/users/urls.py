from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignUpView, TokenObtainView, UserViewSet, MeView

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
