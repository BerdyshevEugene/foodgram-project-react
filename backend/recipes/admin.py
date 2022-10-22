from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, IngredientAmount,
                     ShoppingCart, Tag, RecipeTag)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    min_num = 1
    extra = 1


class RecipeTagsInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorite')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientAmountInline, RecipeTagsInline)

    def favorite(self, obj):
        return obj.favorite.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
