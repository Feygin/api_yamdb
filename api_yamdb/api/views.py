from api.filters import TitleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import GenericViewSet
from reviews.models import Category, Genre, Title

from api.paginations import ReviewPagination
from api.permissions import IsAdminOrReadOnly
from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleReadSerializer, TitleWriteSerializer)


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = ReviewPagination
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = ReviewPagination
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related("genre", "category").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter  # Correctly assign the filter set
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ReviewPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TitleReadSerializer
        return TitleWriteSerializer

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT."""
        if request.method == "PUT":
            raise MethodNotAllowed(
                "PUT", detail="PUT method is not allowed for this endpoint."
            )
        return super().update(request, *args, **kwargs)
