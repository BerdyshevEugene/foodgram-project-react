from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='название'
    )
    color = models.CharField(
        'цвет',
        max_length=7,
        null=True,
        unique=True
    )
    slug = models.SlugField(
        max_length=20,
        unique=True,
        verbose_name='уникальный адрес тэга'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='единица измерения'
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
        verbose_name='изображение',
    )
    text = models.TextField(
        verbose_name='текстовое описание',
        blank=True,
        help_text='введите текст'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='ингридиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингридиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='кол-во ингридиентов'
    )

    class Meta:
        verbose_name = 'кол-во ингридиента'
        verbose_name_plural = 'кол-во ингридиентов'

    def __str__(self):
        return f'{self.ingredient} * {self.amount}'


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='added_recipe',
        verbose_name='добавленный рецепт',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='users_shopping_cart'
        )]
        ordering = ['-id']
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'рецепты в корзине'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='добавленный в избранное',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='users_favorite'
        )]
        ordering = ['-id']
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
