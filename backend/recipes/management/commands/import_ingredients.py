from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import json
from pathlib import Path


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из JSON-файла'

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent 
        path = base_dir / 'data' / 'ingredients.json'
        if not path.exists():
            self.stdout.write(self.style.ERROR(f'Файл {path} не найден.'))
            return

        with open(path, encoding='utf-8') as f:
            data = json.load(f)

        existing = set(
            Ingredient.objects.values_list('name', 'measurement_unit')
        )

        new_ingredients = []
        for item in data:
            key = (item['name'], item['measurement_unit'])
            if key not in existing:
                new_ingredients.append(Ingredient(**item))
                existing.add(key)

        Ingredient.objects.bulk_create(new_ingredients)

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено {len(new_ingredients)} новых ингредиентов из {path.name}'
        ))
