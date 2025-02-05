from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from recipes.constants import (MAX_RECIPE_NAME_LENGTH, MAX_VIEW_LENGTH,
                               MIN_COOKING_TIME, MIN_INGREDIENT_COUNT,
                               SHORT_LINK_MAX_LENGTH, SOME_RESRICTION)

User = get_user_model()


class Tags(models.Model):
    """Модель тэгов"""

    name = models.CharField(
        verbose_name='Имя тэга',
        unique=True,
        max_length=SOME_RESRICTION
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=SOME_RESRICTION
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class Ingredients(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        verbose_name='Наименование ингридиента',
        max_length=SOME_RESRICTION
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=SOME_RESRICTION
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class Recipes(models.Model):
    """ Модель рецептов """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LENGTH
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Картинка блюда',
        upload_to='images',
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),),
        verbose_name='Время готовки'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        default=timezone.now,
        db_index=True
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тэги',
        through='RecipeTag'
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка',
        max_length=SHORT_LINK_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class RecipeIngredient(models.Model):
    """Модель ингридиентов для рецепта"""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество объем',
        validators=[MinValueValidator(MIN_INGREDIENT_COUNT)]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент Рецепта'
        verbose_name_plural = 'Ингредиенты Рецептов'


class RecipeTag(models.Model):
    """Модель тэгов для рецепта"""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        verbose_name='Тэг'
    )

    class Meta:
        default_related_name = 'recipe_tags'
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'


class BaseFavoriteShoppingCart(models.Model):
    """Базовая модель для избранного и корзины"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        default=timezone.now,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_recipe'
            )
        ]


class Favorite(BaseFavoriteShoppingCart):
    """Избранные рецепты"""

    class Meta:
        default_related_name = 'user_favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'Избранные рецепт: {self.recipe} пользователя {self.user}'


class ShoppingCart(BaseFavoriteShoppingCart):
    """Корзина заказов"""

    class Meta:
        default_related_name = 'cart_recipes'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f'Рецепт: {self.recipe} в корзине пользователя {self.user}'
