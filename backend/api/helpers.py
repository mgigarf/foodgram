import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import pagination, serializers

from recipes.constants import PAGE_SIZE


class Base64ImageField(serializers.ImageField):
    """Превращаем картинку из запроса в картинку-файл."""

    def to_internal_value(self, data):
        """Преобразует строку base64 в ImageField."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, image = data.split(';base64,')
            data = ContentFile(
                base64.b64decode(image), name=f'{uuid.uuid4()}.jpg'
            )
        return super().to_internal_value(data)


class ShortLink:

    def create_short_link(self, length):
        return str(uuid.uuid4()).replace('-', '')[:length]


class Pagination(pagination.PageNumberPagination):
    """Класс для пагинации."""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
