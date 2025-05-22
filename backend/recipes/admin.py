from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from .models import (
    Recipe, Ingredient, RecipeIngredient,
    Favorite, ShoppingCart, Subscription
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class CookingTimeFilter(SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time_range'

    def lookups(self, request, model_admin):
        times = Recipe.objects.values_list('cooking_time', flat=True).order_by()
        if not times:
            return ()
        n = times[int(len(times) * 0.33)]
        m = times[int(len(times) * 0.66)]
        return [
            (f'lt_{n}', f'быстрее {n} мин ({Recipe.objects.filter(cooking_time__lt=n).count()})'),
            (f'range_{n}_{m}', f'от {n} до {m} мин ({Recipe.objects.filter(cooking_time__gte=n, cooking_time__lte=m).count()})'),
            (f'gt_{m}', f'дольше {m} мин ({Recipe.objects.filter(cooking_time__gt=m).count()})'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value.startswith('lt_'):
                limit = int(value.split('_')[1])
                return queryset.filter(cooking_time__lt=limit)
            if value.startswith('range_'):
                n, m = map(int, value.split('_')[1:])
                return queryset.filter(cooking_time__gte=n, cooking_time__lte=m)
            if value.startswith('gt_'):
                limit = int(value.split('_')[1])
                return queryset.filter(cooking_time__gt=limit)
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'show_favorites_count', 'show_ingredients', 'show_image'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('author', CookingTimeFilter)
    inlines = [RecipeIngredientInline]
    readonly_fields = ('show_favorites_count', 'show_image')

    @admin.display(description='Добавлений в избранное')
    def show_favorites_count(self, recipe):
        return recipe.favorited_by.count()

    @admin.display(description='Продукты')
    def show_ingredients(self, recipe):
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        return ', '.join([
            f'{ing.ingredient.name} ({ing.amount}{ing.ingredient.measurement_unit})'
            for ing in ingredients
        ])

    @admin.display(description='Картинка')
    def show_image(self, recipe):
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}" width="80" height="80" />')
        return 'Нет изображения'


class HasRecipesFilter(SimpleListFilter):
    title = 'Есть в рецептах'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Используются в рецептах'),
            ('no', 'Не используются'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(recipe__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(recipe__isnull=True)
        return queryset


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', HasRecipesFilter)

    @admin.display(description='В рецептах')
    def recipes_count(self, ingredient):
        return ingredient.recipe.count()
