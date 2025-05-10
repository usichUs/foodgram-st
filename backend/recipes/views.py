from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .filters import RecipeFilter
from .models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)
from .pagination import CustomPagination
from .serializers import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    IngredientSerializer,
    TagSerializer,
    ShortRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    RecipeImageSerializer
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только для автора."""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        
        if request.method == 'POST':
            _, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в списке покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        
        if request.method == 'POST':
            _, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        text = 'Список покупок:\n\n'
        text += '\n'.join([
            f"• {ing['ingredient__name']} "
            f"({ing['ingredient__measurement_unit']}) — {ing['total']}"
            for ing in ingredients
        ])

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
    
    @action(
        detail=True,
        methods=['patch'],
        url_path='upload-image',
        parser_classes=[MultiPartParser],  # Вот он!
        permission_classes=[IsAuthenticated]
    )
    def upload_image(self, request, pk=None):
        """Загрузка изображения для рецепта."""
        recipe = self.get_object()
        
        if 'image' not in request.data:
            return Response(
                {'error': 'Нужно передать файл изображения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeImageSerializer(
            recipe,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None