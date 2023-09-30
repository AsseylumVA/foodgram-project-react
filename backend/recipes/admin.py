from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Ingredient,
                            Recipe,
                            Tag)


class IngredientResource(ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


class RecipeAdmin(ImportExportModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorites_amount')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')

    def favorites_amount(self, obj):
        return obj.favorites.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
