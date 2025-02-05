import django_filters
from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='icontains'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )
    is_favorited = django_filters.NumberFilter(method='get_is_in_favorite')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(cart_recipes__user=self.request.user)
        return queryset

    def get_is_in_favorite(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(user_favorite__user=self.request.user)
        return queryset
