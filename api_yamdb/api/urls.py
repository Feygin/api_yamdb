from django.urls import include, path

from rest_framework import routers

from .views import ReviewViewSet, CommentViewSet

api_v1_router = routers.DefaultRouter

api_v1_router.register(r'reviews', ReviewViewSet, basename='reviews')
api_v1_router.register(r'reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='comments')

urlpatterns = [
    path(r'titles/<int:title_id>/', include((api_v1_router.urls, 'api_v1'))),
]
