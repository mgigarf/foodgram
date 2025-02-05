import json

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from foodgram_backend.settings import PATH_TO_INGREDIENTS
from recipes.models import Ingredient


class Command(BaseCommand):
    """Заполнение базы ингридиентами"""

    def handle(self, *args, **options):

        with open(PATH_TO_INGREDIENTS, encoding='UTF-8') as ingrrdietnds_file:
            ingredients = json.load(ingrrdietnds_file)

            for ingridient in tqdm(ingredients):
                try:
                    Ingredient.objects.get_or_create(**ingridient)
                except CommandError as e:
                    raise CommandError(
                        f'При добавлении {ingridient} '
                        f'произшла ошибка {e}'
                    )
