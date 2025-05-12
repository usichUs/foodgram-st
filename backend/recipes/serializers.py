from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import Recipe, Ingredient, Tag, RecipeIngredient
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, write_only=True)
    ingredients_read = serializers.SerializerMethodField(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author',
            'ingredients', 'ingredients_read',
            'tags', 'image', 'name', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def to_representation(self, instance):
        request = self.context.get('request')

        return {
            'id': instance.id,
            'author': UserSerializer(instance.author, context=self.context).data,
            'ingredients': RecipeIngredientReadSerializer(
                RecipeIngredient.objects.filter(recipe=instance),
                many=True
            ).data,
            'is_favorited': self.get_is_favorited(instance),
            'is_in_shopping_cart': self.get_is_in_shopping_cart(instance),
            'name': instance.name,
            'image': request.build_absolute_uri(instance.image.url) if instance.image and request else None,
            'text': instance.text,
            'cooking_time': instance.cooking_time
        }


    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ids = [item['id'].id for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        return value

    def validate_tags(self, value):
        if value and len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Это поле обязательно.")
        return value
    
    def get_ingredients_read(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientReadSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.in_shopping_cart.filter(user=user).exists()

    def create_ingredients(self, recipe, ingredients):
        for item in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)

        return instance
    
    def validate(self, attrs):
        if self.instance and self.context['request'].method in ('PUT', 'PATCH'):
            if 'ingredients' not in self.initial_data:
                raise serializers.ValidationError({
                    'ingredients': 'Нужен хотя бы один ингредиент.'
                })
        return super().validate(attrs)


class ShortLinkSerializer(serializers.Serializer):
    short_link = serializers.CharField(source='short-link')
