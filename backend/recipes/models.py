from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)
    color = models.CharField(max_length=16, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(
        max_length=24
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/images/',
        default=None
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        null=True,
        on_delete=models.SET_NULL
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    cooking_time = models.PositiveSmallIntegerField('Время приготовления',)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients',)
    amount = models.IntegerField('Количество', null=True)


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart')
