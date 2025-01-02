from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Фильтр для произведения."""
    category = filters.CharFilter(
        field_name="category__slug", lookup_expr="exact")
    genre = filters.CharFilter(field_name="genre__slug", lookup_expr="exact")
    year = filters.NumberFilter(field_name="year", lookup_expr="exact")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Title
        fields = ["category", "genre", "year", "name"]
