from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from api.paginators import PageLimitPagination
from api.serializers import (IngredientSerializer,
                             TagSerializer,
                             RecipeSerializer,)
from recipes.models import (Ingredient,
                            Recipe,
                            Tag,)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    # filter_backends = (DjangoFilterBackend,)
    pagination_class = PageLimitPagination
