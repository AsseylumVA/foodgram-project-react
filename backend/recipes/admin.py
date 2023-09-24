from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from recipes.models import (Ingredient,
                            Recipe,
                            Tag)


class IngredientResource(ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource


class TagResource(ModelResource):
    class Meta:
        model = Tag


class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource


class RecipeResource(ModelResource):
    class Meta:
        model = Recipe


class RecipeAdmin(ImportExportModelAdmin):
    resource_class = RecipeResource


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
