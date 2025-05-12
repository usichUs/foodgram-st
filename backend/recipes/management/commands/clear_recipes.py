from django.core.management.base import BaseCommand
from recipes.models import Recipe

class Command(BaseCommand):
    help = 'Удаляет все рецепты из базы данных'

    def handle(self, *args, **kwargs):
        count, _ = Recipe.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено {count} рецептов.'))
