from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import (Tag, Ingredient, Recipe, IngredientAmount,
                            Favorite, Shopping_cart)
from users.models import Subscribe, User


class UserRegistrationSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context.get('request').user
        subscribing_id = self.data.get['author'].id
        if Subscribe.objects.filter(user=user,
                                    subscribing__id=subscribing_id).exists():
            raise serializers.ValidationError(
                'вы уже подписаны на этого пользователя')
        if user.id == subscribing_id:
            raise serializers.ValidationError(
                'нельзя подписаться на самого себя')
        if user.id is None:
            raise serializers.ValidationError(
                'пользователь не существует')
        return data


class SubscribingRecipesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeViewSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return Subscribe.objects.filter(
            author=obj, user=self.context['request'].user).exists()

    def get_recipes(self, obj):
        recipes_limit = int(self.context['request'].GET.get(
            'recipes_limit', settings.RECIPES_LIMIT))
        user = get_object_or_404(User, pk=obj.pk)
        recipes = Recipe.objects.filter(author=user)[:recipes_limit]

        return SubscribingRecipesSerializers(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        return Recipe.objects.filter(author=user).count()


# class SubscribeSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()
#     recipes_count = SerializerMethodField()
#     recipes = SerializerMethodField()

#     class Meta(CustomUserSerializer.Meta):
#         fields = CustomUserSerializer.Meta.fields + (
#             'recipes_count', 'recipes'
#         )
#         read_only_fields = ('email', 'username')

#     def validate(self, data):
#         author = self.instance
#         user = self.context.get('request').user
#         if Subscribe.objects.filter(author=author, user=user).exists():
#             raise ValidationError(
#                 detail='вы уже подписаны на этого пользователя',
#                 code=status.HTTP_400_BAD_REQUEST
#             )
#         if user == author:
#             raise ValidationError(
#                 detail='нельзя подписаться на самого себя',
#                 code=status.HTTP_400_BAD_REQUEST
#             )
#         return data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         limit = request.GET.get('recipes_limit')
#         recipes = obj.recipes.all()
#         if limit:
#             recipes = recipes[:int(limit)]
#         serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
#         return serializer.data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'нужно выбрать минимум 1 ингредиент!')
        for ingredient in ingredients:
            try:
                int(ingredient.get('amount'))
                if int(ingredient.get('amount')) <= 0:
                    raise serializers.ValidationError(
                        'количество должно быть положительным!')
            except Exception:
                raise ValidationError({'amount': 'колличество должно'
                                      'быть числом'})
            check_id = ingredient['id']
            check_ingredient = Ingredient.objects.filter(id=check_id)
            if not check_ingredient.exists():
                raise serializers.ValidationError(
                    'данного продукта нет в базе!')
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        try:
            int(cooking_time)
            if int(cooking_time) < 1:
                raise serializers.ValidationError(
                    'время готовки не может быть меньше 1!')
            if int(cooking_time) > 600:
                raise serializers.ValidationError(
                    'Время готовки не может быть больше 600!')
        except Exception:
            raise serializers.ValidationError({'cooking_time': 'Время'
                                               ' должно быть больше 0'})
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Рецепт не может быть без тегов'
            )
        for tag_id in tags:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'Тег с id = {tag_id} не существует'
                )
        tags_bd = set(tags)
        if len(tags) != len(tags_bd):
            raise ValidationError('Теги должны быть уникальными')
        return data

    def create_bulk(self, recipe, ingredients_data):
        IngredientAmount.objects.bulk_create([IngredientAmount(
            ingredient=ingredient['ingredient'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients_data])

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_bulk(recipe, ingredients_data)
        return recipe

    def update(self, recipe, validated_data):
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )
        recipe.image = validated_data.get('image', recipe.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            for ingredient in ingredients:
                IngredientAmount.objects.create(
                    recipe=recipe,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount'],
                )
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)

        representation = super().to_representation(recipe)
        representation['ingredients'] = RecipeIngredientSerializer(
            IngredientAmount.objects.filter(
                recipe=recipe).all(), many=True).data

        return representation


class ShowRecipeFullSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj,
                                       user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Shopping_cart.objects.filter(recipe=obj,
                                           user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True, source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True, source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True, source='recipe.name',
    )

    def validate(self, data):
        recipe = data['recipe']
        user = data['user']
        if user == recipe.author:
            raise serializers.ValidationError(
                'вы не можете добавить свои рецепты в избранное')
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'вы уже добавили рецепт в избранное')
        return data

    def create(self, validated_data):
        """Метод создания избранного"""
        favorite = Favorite.objects.create(**validated_data)
        favorite.save()
        return favorite

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор продуктовой корзины"""
    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = Shopping_cart
        fields = ('id', 'name', 'image', 'cooking_time')


# class RecipeReadSerializer(ModelSerializer):
#     tags = TagSerializer(many=True, read_only=True)
#     author = UserSerializer(read_only=True)
#     ingredients = SerializerMethodField()
#     image = Base64ImageField()
#     is_favorited = SerializerMethodField(read_only=True)
#     is_in_shopping_cart = SerializerMethodField(read_only=True)

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'tags',
#             'author',
#             'ingredients',
#             'is_favorited',
#             'is_in_shopping_cart',
#             'name',
#             'image',
#             'text',
#             'cooking_time',
#         )

#     def get_ingredients(self, obj):
#         recipe = obj
#         ingredients = recipe.ingredients.values(
#             'id',
#             'name',
#             'measurement_unit',
#             amount=F('ingredientamount__amount')
#         )
#         return ingredients

#     def get_is_favorited(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return user.favorites.filter(recipe=obj).exists()

#     def get_is_in_shopping_cart(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return user.shopping_cart.filter(recipe=obj).exists()


class IngredientAmountWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


# class RecipeWriteSerializer(ModelSerializer):
#     tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
#                                   many=True)
#     author = UserSerializer(read_only=True)
#     ingredients = IngredientAmountWriteSerializer(many=True)
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'tags',
#             'author',
#             'ingredients',
#             'name',
#             'image',
#             'text',
#             'cooking_time',
#         )

#     def validate_ingredients(self, value):
#         ingredients = value
#         if not ingredients:
#             raise ValidationError({
#                 'ingredients': 'должен быть как минимум один ингридиент'
#             })
#         ingredients_list = []
#         for item in ingredients:
#             ingredient = get_object_or_404(Ingredient, id=item['id'])
#             if ingredient in ingredients_list:
#                 raise ValidationError({
#                     'ingredients': 'ингридиенты не должны повторяться'
#                 })
#             if int(item['amount']) <= 0:
#                 raise ValidationError({
#                     'amount': 'ингридиентов должно быть больше 0'
#                 })
#             ingredients_list.append(ingredient)
#         return value

#     def validate_tags(self, value):
#         tags = value
#         if not tags:
#             raise ValidationError({
#                 'tags': 'выберите хотя бы один тэг'
#             })
#         tags_set = set(tags)
#         if len(tags) != len(tags_set):
#             raise ValidationError({
#                 'tags': 'тэги должны быть уникальными'
#             })
#         return value

#     def create_ingredients_amounts(self, ingredients, recipe):
#         IngredientAmount.objects.bulk_create(
#             [IngredientAmount(
#                 ingredient=Ingredient.objects.get(id=ingredient['id']),
#                 recipe=recipe,
#                 amount=ingredient['amount']
#             ) for ingredient in ingredients]
#         )

#     @transaction.atomic
#     def create(self, validated_data):
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(**validated_data)
#         recipe.tags.set(tags)
#         self.create_ingredients_amounts(recipe=recipe,
#                                         ingredients=ingredients)
#         return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         instance = super().update(instance, validated_data)
#         instance.tags.clear()
#         instance.tags.set(tags)
#         instance.ingredients.clear()
#         self.create_ingredients_amounts(recipe=instance,
#                                         ingredients=ingredients)
#         instance.save()
#         return instance

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeReadSerializer(instance,
#                                     context=context).data


# class RecipeShortSerializer(ModelSerializer):
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'name',
#             'image',
#             'cooking_time'
#         )
