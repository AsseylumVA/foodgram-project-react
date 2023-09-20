from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)
    color = models.CharField(max_length=16, unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    unit = models.CharField(verbose_name="Единицы измерения", max_length=24)


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
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
        through='RecipeIngredient')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        default=0,
    )


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField('Количество', default=0)
