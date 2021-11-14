from django_filters import rest_framework as filters

from .models import Title


class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug',
                                  lookup_expr='icontains')
    genre = filters.CharFilter(field_name='genre__slug',
                               lookup_expr='icontains')
    year = filters.NumberFilter(field_name='year')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'year', 'name']
