from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet, MeView,
                       SignUpView, TokenObtainView, UserViewSet)

api_v1_router = DefaultRouter()

api_v1_router.register(
    r'genres',
    GenreViewSet,
    basename='genre'
)
api_v1_router.register(
    r'categories',
    CategoryViewSet,
    basename='category'
)
api_v1_router.register(
    r'titles',
    TitleViewSet,
    basename='title'
)
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
api_v1_router.register(
    r'users',
    UserViewSet,
    basename='users'
)

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('v1/users/me/', MeView.as_view(), name='me'),
    path('v1/', include((api_v1_router.urls, 'api_v1'))),
]
