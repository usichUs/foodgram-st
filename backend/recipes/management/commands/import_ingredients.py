import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из JSON-фикстуры'

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        path = base_dir / 'data' / 'ingredients.json'

        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            ingredients = [
                Ingredient(name=item['name'], measurement_unit=item['measurement_unit'])
                for item in data
            ]

            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                f'Импортировано {len(ingredients)} ингредиентов из {path.name}'
            ))

        except Exception as e:
            raise CommandError(f'Ошибка при импорте из {path.name}: {e}')

