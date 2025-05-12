from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.contrib.auth import get_user_model

from .models import (
    Recipe, Ingredient, Tag,
    ShoppingCart, Favorite, RecipeIngredient
)
from .serializers import (
    RecipeSerializer, ShortRecipeSerializer,
    TagSerializer, IngredientSerializer, ShortLinkSerializer
)
from .pagination import CustomPagination
from .filters import RecipeFilter

import io

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update',
                           'destroy', 'favorite', 'shopping_cart',
                           'download_shopping_cart']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['favorite', 'shopping_cart']:
            return ShortRecipeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        recipe = self.get_object()
        if recipe.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("У вас недостаточно прав для выполнения данного действия.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой рецепт.")
        instance.delete()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        author = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')

        if author:
            queryset = queryset.filter(author__id=author)

        if user.is_authenticated:
            if is_favorited == '1':
                queryset = queryset.filter(favorited_by__user=user)
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(in_shopping_cart__user=user)

        return queryset

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном."},
                    status=400
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=201)
        deleted, _ = Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted:
            return Response(status=204)
        return Response(
            {"errors": "Рецепта не было в избранном."},
            status=400
        )

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в корзине."},
                    status=400
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=201)
        deleted, _ = ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted:
            return Response(status=204)
        return Response(
            {"errors": "Рецепта не было в корзине."},
            status=400
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        lines = [
            f'{item["ingredient__name"]} ({item["ingredient__measurement_unit"]}) — {item["total"]}'
            for item in ingredients
        ]
        content = '\n'.join(lines)
        buffer = io.BytesIO()
        buffer.write(content.encode())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shopping_list.txt')
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def get_link(self, request, pk=None):
        try:
            recipe = self.get_object()
        except Http404:
            raise NotFound(detail="Страница не найдена.")

        short_code = f"3d{recipe.id}"
        full_url = f"https://foodgram.example.org/s/{short_code}"

        return Response({'short-link': full_url}, status=200)
