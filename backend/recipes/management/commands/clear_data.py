from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import (
    Recipe, Tag, Subscription,
    ShoppingCart, Favorite, RecipeIngredient
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Удаляет все тестовые данные, кроме ингредиентов'

    def handle(self, *args, **kwargs):
        self.stdout.write('Удаление данных...')

        Favorite.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Subscription.objects.all().delete()
        RecipeIngredient.objects.all().delete()
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS('✅ Всё очищено, кроме ингредиентов'))
