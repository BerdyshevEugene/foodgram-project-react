from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, download_shopping_cart)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
