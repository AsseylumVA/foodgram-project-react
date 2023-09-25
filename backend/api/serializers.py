import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientRecipe,
                            Favorite)
from users.serializers import CustomUserSerializer


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
        return False


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=MIN_INGREDIENT_AMOUNT,
                message=(f'Количество ингредиента не может быть '
                         f'меньше {MIN_INGREDIENT_AMOUNT}')
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
        unique_tags = list(set(tags))
        if len(tags) != len(unique_tags):
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
