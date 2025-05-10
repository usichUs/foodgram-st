from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from recipes.models import Subscription
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            're_password'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        logger.debug(f"Validating data: {attrs}")
        if attrs['password'] != attrs['re_password']:
            logger.error("Passwords do not match")
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            logger.error(f"Password validation failed: {e.messages}")
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def validate_email(self, value):
        if not value or '@' not in value or '.' not in value:
            logger.error(f"Invalid email format: {value}")
            raise serializers.ValidationError("Некорректный формат email.")
        return value.lower()  # Нормализуем email

    def validate_username(self, value):
        if not value or len(value) > 150:
            logger.error(f"Invalid username: {value}")
            raise serializers.ValidationError("Имя пользователя слишком длинное или пустое (максимум 150 символов).")
        return value

    def validate_first_name(self, value):
        if not value or len(value) > 150:
            logger.error(f"Invalid first_name: {value}")
            raise serializers.ValidationError("Имя слишком длинное или пустое (максимум 150 символов).")
        return value

    def validate_last_name(self, value):
        if not value or len(value) > 150:
            logger.error(f"Invalid last_name: {value}")
            raise serializers.ValidationError("Фамилия слишком длинная или пустая (максимум 150 символов).")
        return value

    def create(self, validated_data):
        validated_data.pop('re_password')
        logger.info(f"Creating user with email: {validated_data['email']}")
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, author=obj).exists()

class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['recipes', 'recipes_count']

    def get_recipes(self, obj):
        from recipes.serializers import ShortRecipeSerializer
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            try:
                queryset = queryset[:int(recipes_limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
