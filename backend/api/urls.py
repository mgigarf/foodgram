from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipesViewSet, TagViewSet, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipesViewSet, 'recipe')
router.register('users', UserViewSet, 'user')
router.register('tags', TagViewSet, 'tag'),
router.register('ingredients', IngredientViewSet, 'ingredient')


api_urls = [
    path('', include(router.urls)),
]

auth_urls = [path('', include('djoser.urls.authtoken'))]

urlpatterns = [
    path('', include(api_urls)),
    path('auth/', include(auth_urls))
]
