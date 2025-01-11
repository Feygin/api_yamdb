from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet)

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

urlpatterns = [
    path('v1/', include((api_v1_router.urls, 'api_v1'))),
]
