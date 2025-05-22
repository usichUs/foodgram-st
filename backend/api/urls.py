from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.recipes import RecipeViewSet, IngredientViewSet
from api.views.users import UserViewSet

recipe_link = RecipeViewSet.as_view({'get': 'get_link'})

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:pk>/get-link/', recipe_link),
]
