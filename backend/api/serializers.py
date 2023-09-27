import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientRecipe,
                            Favorite)
from users.models import Subscription
from users.serializers import CustomUserSerializer

User = get_user_model()

MIN_INGREDIENT_AMOUNT = 1


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             read_only=True,
                                             source='recipe_ingredients')
    image = serializers.SerializerMethodField('get_image_url', read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        if not self.context:
            return False
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context:
            return False
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message=('Количество ингредиента не может быть меньше 1')
            ),
        )
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientRecipePostSerializer(
        many=True,
        source='recipe_ingredients'
        )
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            limit_value=1,
            message=('Время приготовление не должно быть меньше 1')
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'errors': 'Не добавлены теги'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'errors': 'Добавлены одинаковые теги'}
            )
        if not data.get('recipe_ingredients'):
            raise serializers.ValidationError(
                {'errors': 'Не добавлены ингредиенты'}
            )
        ingredients = list(map(lambda x: x['id'],
                               data.get('recipe_ingredients')))
        if len(set(ingredients)) != len(ingredients):
            raise serializers.ValidationError(
                {'errors': 'нельзя добавить два одинаковых ингредиента'}
            )

        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient_obj = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient_obj, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()

        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags_data)

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        for ingredient_data in ingredients_data:
            ingredient_obj = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient_obj, amount=amount
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data


class ReceipSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        serializer = ReceipSmallSerializer(instance.recipe)
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeReprSerializer(instance.author,
                                       context={'request': request}).data


class SubscribeReprSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username',
                            'first_name', 'last_name', 'is_subscribed',
                            'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return ReceipSmallSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
