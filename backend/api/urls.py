from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, ListSubscribeViewSet, SubscribeApiView)

app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', SubscribeApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', ListSubscribeViewSet.as_view(),
         name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
