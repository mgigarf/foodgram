from django.core.exceptions import ValidationError

from .constants import NOT_ALLOWED_USER_NAME


def not_allowed_user_name(value):
    if value in NOT_ALLOWED_USER_NAME:
        raise ValidationError(
            f'{value} запрещенное значение для ника пользователя'
        )
    return value
