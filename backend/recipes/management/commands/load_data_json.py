import logging
import json

from django.apps import apps
from django.core.management import BaseCommand

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


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
        model = apps.get_model(options['app_name'], options['model_name'])
        with open(options['path'], 'rt', encoding='utf-8') as f:
            instance_data = json.load(f)
            instances = [model(**x) for x in instance_data]
            model.objects.bulk_create(instances)
            logging.info(f'Data loaded successfully. Created {len(instances)} '
                         f'{model.__name__}''s')
