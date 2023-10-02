from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeSerializer,
                          ReceipSmallSerializer,
                          RecipeCreateSerializer,
                          SubscribeSerializer,
                          SubscribeReprSerializer)
from recipes.models import (Ingredient,
                            IngredientRecipe,
                            Recipe,
                            Tag)
from users.models import Subscription
from errors import (RECIPE_FAVORITE_ERROR, SHOPPING_CART_ALLREADY_IN_ERROR,
                    SHOPPING_CART_NOT_IN_ERROR, SUBSCRIBE_ERROR)

User = get_user_model()


class UserSubscribeView(APIView):
    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        if not Subscription.objects.filter(user=request.user,
                                           author__id=user_id).exists():
            return Response(
                {'errors': SUBSCRIBE_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(user=request.user.id,
                                 author=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscribeReprSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    queryset = Tag.objects.all()
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': pk,
        }
        serializer = FavoriteSerializer(data=data)
        if request.method == 'POST':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        if not user.favorites.filter(recipe=recipe).exists():
            data = {
                'error': RECIPE_FAVORITE_ERROR
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        user.favorites.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                data = {
                    'error': SHOPPING_CART_ALLREADY_IN_ERROR
                }
                return Response(data, status.HTTP_400_BAD_REQUEST)
            user.shopping_cart.create(recipe=recipe)
            serializer = ReceipSmallSerializer(recipe)
            return Response(serializer.data, status.HTTP_201_CREATED)

        if not user.shopping_cart.filter(recipe=recipe).exists():
            data = {
                'error': SHOPPING_CART_NOT_IN_ERROR
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, pk=None):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = [' - '.join(map(str, x.values())) for x in ingredients]
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
