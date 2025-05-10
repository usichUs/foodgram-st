from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite, RecipeIngredient
from .serializers import RecipeSerializer, ShortRecipeSerializer, TagSerializer, IngredientSerializer
from .pagination import CustomPagination
from django.contrib.auth import get_user_model
import io
from django.db.models import Sum
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'favorite', 'shopping_cart']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['favorite', 'shopping_cart']:
            return ShortRecipeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if 'is_favorited' in self.request.query_params and self.request.query_params['is_favorited'] == '1':
                queryset = queryset.filter(favorited_by__user=user)
            if 'is_in_shopping_cart' in self.request.query_params and self.request.query_params['is_in_shopping_cart'] == '1':
                queryset = queryset.filter(in_shopping_cart__user=user)
        if 'author' in self.request.query_params:
            queryset = queryset.filter(author__id=self.request.query_params['author'])
        if 'tags' in self.request.query_params:
            tags = self.request.query_params.getlist('tags')
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            _, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепт не в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            _, created = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not cart.exists():
            return Response(
                {'errors': 'Рецепт не в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        buffer = io.StringIO()
        buffer.write("Список покупок:\n\n")
        for item in ingredients:
            buffer.write(
                f"{item['ingredient__name']} ({item['ingredient__measurement_unit']}): {item['total_amount']}\n"
            )
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', '').lower()
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
