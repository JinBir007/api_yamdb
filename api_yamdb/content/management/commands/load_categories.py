import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from content.models import Category


class Command(BaseCommand):
    """Команда для загрузки данных категорий из CSV-файла в базу данных."""

    help = 'Загружает категории из CSV-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV-файлу с категориями')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row['name']
                    slug = row.get('slug')
                    if not slug:
                        slug = slugify(name)
                    if Category.objects.filter(slug=slug).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Категория со slug "{slug}" уже существует.'
                                f'Пропускаем.')
                        )
                        continue
                    category = Category(name=name, slug=slug)
                    category.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Успешно добавлена категория: {name} ({slug})'
                        )
                    )
        except FileNotFoundError:
            raise CommandError(f'Файл "{csv_file_path}" не найден.')
        except Exception as e:
            raise CommandError(f'Ошибка при обработке файла: {e}')
