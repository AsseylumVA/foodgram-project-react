import json

from django.apps import apps
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Creating model objects according the file path specified'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help="file path")
        parser.add_argument('--model_name', type=str, help="model name")
        parser.add_argument(
            '--app_name',
            type=str,
            help="django app name that the model is connected to"
        )

    def handle(self, *args, **options):
        file_path = options['path']
        model = apps.get_model(options['app_name'], options['model_name'])
        with open(file_path, 'rt', encoding='utf-8') as f:
            ingredients_data = json.load(f)
            instances = [model(**x) for x in ingredients_data]
            model.objects.bulk_create(instances)
            print(f'data loaded successfully. Created {len(instances)} '
                  f'{model.__name__}''s')
