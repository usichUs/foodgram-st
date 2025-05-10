import csv
import os
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла в модель Ingredient'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV файлу с данными об ингредиентах'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        if not os.path.exists(csv_file_path):
            logger.error(f"Файл {csv_file_path} не найден")
            raise CommandError(f"Файл {csv_file_path} не найден")

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                expected_headers = {'name', 'measurement_unit'}
                if not expected_headers.issubset(reader.fieldnames):
                    logger.error("CSV файл должен содержать колонки 'name' и 'measurement_unit'")
                    raise CommandError("CSV файл должен содержать колонки 'name' и 'measurement_unit'")

                created_count = 0
                skipped_count = 0

                for row in reader:
                    name = row['name'].strip()
                    measurement_unit = row['measurement_unit'].strip()

                    if not name or not measurement_unit:
                        logger.warning(f"Пропущена запись с пустыми полями: {row}")
                        skipped_count += 1
                        continue

                    if len(name) > 200 or len(measurement_unit) > 20:
                        logger.warning(f"Пропущена запись с превышением длины полей: {row}")
                        skipped_count += 1
                        continue

                    try:
                        ingredient, created = Ingredient.objects.get_or_create(
                            name=name,
                            defaults={'measurement_unit': measurement_unit}
                        )
                        if created:
                            created_count += 1
                            logger.info(f"Создан ингредиент: {ingredient}")
                        else:
                            skipped_count += 1
                            logger.info(f"Ингредиент уже существует: {ingredient}")

                    except Exception as e:
                        logger.error(f"Ошибка при создании ингредиента {name}: {str(e)}")
                        skipped_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Импорт завершен: создано {created_count} ингредиентов, "
                        f"пропущено {skipped_count} записей"
                    )
                )

        except Exception as e:
            logger.error(f"Ошибка при импорте данных: {str(e)}")
            raise CommandError(f"Ошибка при импорте данных: {str(e)}")
