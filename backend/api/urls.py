from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet, IngredientViewSet,
                    RecipeViewSet, ListSubscribeViewSet, SubscribeApiView)

app_name = 'api'

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('users/<int:id>/subscribe/', SubscribeApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', ListSubscribeViewSet.as_view(),
         name='subscriptions'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
