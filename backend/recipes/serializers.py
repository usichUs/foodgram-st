from rest_framework import serializers
from .models import Recipe, Ingredient, Tag, RecipeIngredient, ShoppingCart, Favorite
from users.models import User
from .fields import validate_image

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта и ингредиента."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'image', 
            'text', 'cooking_time', 'ingredients', 
            'tags'
        ]

class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецептов."""
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    ingredients = serializers.JSONField()
    tags = serializers.ListField()
    image = serializers.ImageField(
        validators=[validate_image],
        required=True,
        allow_null=False
    )

    class Meta:
        model = Recipe
        fields = [
            'image', 'id', 'name', 'author', 'image', 
            'text', 'cooking_time', 'ingredients', 
            'tags'
        ]

    def validate_author(self, value):
        if value != self.context['request'].user:
            raise serializers.ValidationError(
                "Вы можете создавать рецепты только от своего имени"
            )
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        
        recipe.tags.set(tags_data)
        return recipe
    

class ShortRecipeSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для избранного и корзины."""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
    recipe = ShortRecipeSerializer()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    recipe = ShortRecipeSerializer()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']