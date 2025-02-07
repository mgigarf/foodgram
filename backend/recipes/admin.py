from django.contrib import admin

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            ShoppingCart, Tag)


class IngredientsInline(admin.TabularInline):
    """Инлайн для ингредиентов."""

    model = RecipeIngredient
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов"""

    list_display = (
        'name',
        'get_username',
        'text',
        'image',
        'cooking_time',
        'get_ingredients',
        'get_tags',
        'pub_date',
        'get_favorite_count',
    )
    search_fields = (
        'author__username',
        'name'
    )
    list_filter = ('name', 'tags',)
    filter_horizontal = ('tags',)
    inlines = [IngredientsInline]

    @admin.display(description='Автор')
    def get_username(self, object):
        return object.author.username

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, object):
        return '\n'.join(
            obj.ingredient.name for obj in object.recipe_ingredients.all()
        )

    @admin.display(description='Тэги')
    def get_tags(self, object):
        return '\n'.join(
            obj.name for obj in object.tags.all()
        )

    @admin.display(description='Сколько раз добавили в избранное')
    def get_favorite_count(self, object):
        return object.user_favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка Ингридиента."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )

    list_editable = (
        'name',
        'measurement_unit',
    )

    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка Избранного."""

    list_display = (
        'id',
        'user',
        'recipe',
        'pub_date',
    )

    list_editable = (
        'user',
        'recipe',
    )

    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка Корзины."""

    list_display = (
        'id',
        'user',
        'recipe',
        'pub_date',
    )

    list_editable = (
        'user',
        'recipe',
    )

    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Админка Тэгов."""

    list_display = (
        'id',
        'name',
        'slug',
    )

    list_editable = (
        'name',
        'slug',
    )

    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка Рецепто-ингрединтов."""

    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount'
    )

    list_editable = (
        'recipe',
        'ingredient',
        'amount'
    )

    search_fields = (
        'recipe__name',
        'ingredient__name',
    )
    list_filter = (
        'recipe',
        'ingredient',
    )


admin.site.empty_value_display = 'Не задано'
