from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Админка пользователя"""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )

    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка подписок"""

    list_display = (
        'id',
        'user',
        'following',
    )

    search_fields = ('user__username', 'author__username')
    list_editable = ('user', 'following')
    list_filter = ('user', 'following')


admin.site.empty_value_display = 'Нет значения'
