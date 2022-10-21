from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Tag, Ingredient, Recipe, IngredientAmount,
                            Shoppping_cart, Favorite)
from users.models import Subscribe
from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import (AdminPermission, IsAuthorOrReadOnly)
from .serializers import (SubscribeSerializer, TagSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          CustomUserSerializer)

from .serializers import SubscribeViewSerializer
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
User = get_user_model()


class SubscribeApiView(APIView):
    """APIView подписки/отписка на автора"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        author = get_object_or_404(User, pk=pk)
        user = request.user
        obj = Subscribe(author=author, user=user)
        obj.save()

        serializer = SubscribeViewSerializer(
            author, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        try:
            subscription = get_object_or_404(Subscribe, user=user,
                                             auhor=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscribe.DoesNotExist:
            return Response(
                'ошибка отписки',
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListSubscribeViewSet(generics.ListAPIView):
    """Лист подписчиков"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscribeViewSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscribing__user=user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminPermission, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Shoppping_cart, request.user, pk)
        else:
            return self.delete_from(Shoppping_cart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'рецепт уже удален'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view()
def download_shopping_cart(request):
    baskets = Shoppping_cart.objects.filter(user=request.user)
    cart_list = {}
    for basket in baskets:
        for ingredient in basket.recipy.ingredients.all():
            amount = get_object_or_404(
                IngredientAmount,
                recipy=basket.recipy,
                ingredient=ingredient
            ).amount
            if ingredient.name not in cart_list:
                cart_list[ingredient.name] = amount
            else:
                cart_list[ingredient.name] += amount

    content = 'список покупок:\n\n'
    if not cart_list:
        content += 'корзина пуста'
    for item in cart_list:
        measurement_unit = get_object_or_404(
            Ingredient,
            name=item
        ).measurement_unit
        content += f'{item}: {cart_list[item]} {measurement_unit}\n'

    response = HttpResponse(
        content, content_type='text/plain,charset=utf8'
    )
    response['Content-Disposition'] = 'attachment; filename="shop_cart.txt"'
    return response
