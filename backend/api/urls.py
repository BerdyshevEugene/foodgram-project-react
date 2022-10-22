from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, ListSubscribeViewSet, SubscribeApiView)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
     path(
        r'recipes/<recipe_id>/favorite/',
        RecipeViewSet.as_view({
            'post': 'create',
            'delete': 'delete'
        }),
        name='favorite'),
    path(
        r'recipes/<recipe_id>/shopping_cart/',
        RecipeViewSet.as_view({
            'post': 'create',
            'delete': 'delete'
        }),
        name='shopping_cart'),
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', SubscribeApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', ListSubscribeViewSet.as_view(),
         name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
