from django_filters import rest_framework as filters
from .models import Recipe
from users.models import User

class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorited(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorited_by__user=self.request.user)
            return queryset.none()
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(in_shopping_cart__user=self.request.user)
            return queryset.none()
        return queryset
