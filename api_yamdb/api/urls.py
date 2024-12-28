from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, CommentViewSet

api_v1_router = DefaultRouter()

api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('api/v1/', include((api_v1_router.urls, 'api_v1'))),
]
