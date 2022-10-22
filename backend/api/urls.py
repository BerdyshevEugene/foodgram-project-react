from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser import views

from .views import (CustomUserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, ListSubscribeViewSet, SubscribeApiView)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('users/<int:id>/subscribe/', SubscribeApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', ListSubscribeViewSet.as_view(),
         name='subscriptions'),
    path('auth/token/login/', views.TokenCreateView.as_view(),
         name='login'),
    path('auth/token/logout/', views.TokenDestroyView.as_view(),
         name='logout'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
