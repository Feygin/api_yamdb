from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import MeView, SignUpView, TokenObtainView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
