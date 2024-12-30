from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, GenreViewSet, TitleViewSet

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


urlpatterns = [
    path('v1/', include((api_v1_router.urls, 'api_v1'))),
]
