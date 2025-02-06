from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.helpers import Base64ImageField
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            RecipeTag, Tag)
from user.constants import MAX_USER_NAME_LENGTH, MIN_PASSWORD_LENGTH
from user.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_followed'
    )
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_followed(self, following):
        user = self.context.get('request').user
        return user.is_authenticated and user.following.filter(
            following=following
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор создания связи Рецепт/Ингридиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получение ингридиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    name = serializers.CharField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'measurement_unit', 'name']


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_in_favorite'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        exclude = ['short_link', 'pub_date']

    def get_is_in_favorite(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.user_favorite.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.cart_recipes.filter(recipe=obj).exists())


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    image = Base64ImageField()
    ingredients = CreateRecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('recipe_ingredients')
        if not tags:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле tags'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле ingredients'
            )
        ingredients_ids = [
            ingredient.get('ingredient').id for ingredient in ingredients
        ]
        if len(set(ingredients_ids)) != len(ingredients):
            raise serializers.ValidationError(
                'Ингридиенты должны быть уникальными'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Тэги должны быть уникальными'
            )
        return attrs

    def create(self, value):
        ingredients = value.pop('recipe_ingredients')
        tags = value.pop('tags')
        recipe = Recipe.objects.create(**value)
        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, **ingredient)
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, value):
        ingredients = value.pop('recipe_ingredients')
        tags = value.pop('tags')
        recipe.recipe_ingredients.all().delete()
        recipe.tags.clear()
        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, **ingredient)
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return super().update(recipe, value)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorite_recipes.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.cart_recipes.filter(recipe=obj).exists())


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(
        min_length=MIN_PASSWORD_LENGTH, write_only=True, required=True)
    first_name = serializers.CharField(
        required=True,
        max_length=MAX_USER_NAME_LENGTH
    )
    last_name = serializers.CharField(
        required=True,
        max_length=MAX_USER_NAME_LENGTH
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'id',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления аватара пользователю."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class GetFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о подписках."""

    recipes = serializers.SerializerMethodField(
        method_name='get_recipe'
    )

    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipe(self, author):
        recipes = author.recipes.all()
        request = self.context.get('request')
        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            if recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.following.filter(following=user).exists())


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]
        model = Follow
        fields = '__all__'

    def validate(self, attrs):
        follower = attrs['user']
        following = attrs['following']

        if follower == following:
            raise serializers.ValidationError(
                'Попытка подписаться на самого себя'
            )
        is_subscription_exists = Follow.objects.filter(
            user=follower,
            following=following
        ).exists()
        if is_subscription_exists:
            raise serializers.ValidationError('Подписка уже есть')
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return GetFollowSerializer(
            instance.author, context={'request': request}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения короткой версии рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCart(serializers.ModelSerializer):
    """Сериализатор для корзины."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
