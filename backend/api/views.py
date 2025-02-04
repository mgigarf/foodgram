from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.helpers import CustomPagination, ShortLink
from api.permissions import OwnerOrReadOnly
from api.serializers import (CreateUserSerializer,
                             FollowSerializer, GetFollowSerializer,
                             GetRecipeSerializer, IngredientSerializer,
                             RecipesSerializer, ShortRecipeSerializer,
                             TagsSerializer, UserAvatarSerializer,
                             UserSerializer)
from recipes.constants import SHORT_LINK_MAX_POSTFIX, URL
from recipes.models import (Favorite, Ingredients, RecipeIngredient, Recipes,
                            ShoppingCart, Tags)
from user.models import Follow

User = get_user_model()


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта и всего что с ним связано"""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly, OwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['GET'],
        url_path='get-link',
        detail=True
    )
    def get_short_link(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        if recipe.short_link:
            return Response(
                {"short-link": URL + recipe.short_link},
                status=status.HTTP_200_OK
            )
        while True:
            short_link = ShortLink().create_short_link(SHORT_LINK_MAX_POSTFIX)
            try_recipe = Recipes.objects.filter(short_link=short_link)
            if not try_recipe:
                break
        recipe.short_link = short_link
        recipe.save()
        short_link = URL + short_link
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        url_path='favorite',
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def add_to_favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                    user=request.user,
                    recipe=recipe
            ).exists():
                return Response(
                    {'add_to_favorite_error': 'Рецепт уже есть в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite:
            return Response(
                {'error': 'в избранном нет такого рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def add_to_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=recipe
            ).exists():
                return Response(
                    {'add_to_favorite_error': 'Рецепт уже есть в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe_in_cart = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if not recipe_in_cart:
            return Response(
                {'error': 'такого рецепта в корзине нет'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_cart_ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart_recipes__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        )

        shopping_list = []
        for item in shopping_cart_ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            total_amount = item['total_amount']
            shopping_list.append(f"{name} ({unit}) — {total_amount}")

        shopping_list_text = "\n".join(shopping_list)
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'

        return response


class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if (
                self.action == 'list'
                or self.action == 'retrieve'
                or self.action == 'me'
        ):
            return UserSerializer
        return super().get_serializer_class()

    @action(
        methods=['GET'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT', 'DELETE'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def user_avatar(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, id):
        user = get_object_or_404(User, username=request.user.username)
        following = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': user.id, 'following': following.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            limit = request.query_params.get('recipes_limit')
            recipes = following.recipes.all()
            if limit:
                recipes = recipes[:int(limit)]
            user_data = UserSerializer(
                following,
                context={'request': request}
            ).data
            user_data['recipes'] = ShortRecipeSerializer(
                recipes, context={'request': request}, many=True
            ).data
            user_data['recipes_count'] = len(user_data['recipes'])
            return Response(user_data, status=status.HTTP_201_CREATED)
        follow = Follow.objects.filter(
            user=user.id,
            following=following.id
        )
        if follow:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def get_subscribtions(self, request):
        user = get_object_or_404(User, username=request.user.username)
        limit = request.query_params.get('limit')
        following_users = User.objects.filter(following__user=user)
        if limit:
            following_users = following_users[:int(limit)]
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(following_users, request)
        serializer = GetFollowSerializer(
            result_page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тэгов"""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов"""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


def redirect_to_recipe_detail(request, short_link_code):
    recipe = get_object_or_404(Recipes, short_link=short_link_code)
    return redirect(
        'api:recipe-detail',
        pk=recipe.id
    )
