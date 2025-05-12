from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Добавляет 3 тега: Завтрак, Обед, Ужин'

    def handle(self, *args, **kwargs):
        tags = [
            {'name': 'Завтрак', 'color': '#FFA500', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#00FF00', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#0000FF', 'slug': 'dinner'},
        ]

        created = 0
        for tag in tags:
            obj, created_flag = Tag.objects.get_or_create(**tag)
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Добавлено {created} тегов'))
