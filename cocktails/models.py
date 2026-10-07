from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_alcoholic = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cocktail(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="CocktailIngredient",
        related_name="cocktails",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cocktails",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="recipe_items",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="recipe_items",
    )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cocktail", "ingredient"],
                name="unique_ingredient_per_cocktail",
            )
        ]

    def __str__(self):
        return f"{self.ingredient}, {self.amount} {self.unit} | {self.cocktail}"