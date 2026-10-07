from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cocktails.models import Cocktail, CocktailIngredient, Ingredient

class CocktailAPITests(APITestCase):

    def setUp(self):

        self.ingredient_1 = Ingredient.objects.create(
            name="Rum", description="Dark rum", is_alcoholic=True
        )
        self.ingredient_2 = Ingredient.objects.create(
            name="Cola", description="Tata jest kola?", is_alcoholic=False
        )

        self.cocktail_url = reverse("cocktail-list")
        self.ingredient_url = reverse("ingredient-list")


    def test_create_cocktail_success(self):
        data = {
            "name": "Cuba Libre",
            "category": "Cocktail",
            "instructions": "Mix rum and cola with ice.",
            "recipe_items": [
                {"ingredient": self.ingredient_1.id, "amount": 50, "unit": "ml"},
                {"ingredient": self.ingredient_2.id, "amount": 150, "unit": "ml"}
            ]
        }

        response = self.client.post(self.cocktail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cocktail.objects.count(), 1)
        self.assertEqual(CocktailIngredient.objects.count(), 2)
        self.assertEqual(Cocktail.objects.get().name, "Cuba Libre")


    def test_create_cocktail_duplicate_ingredients_fails(self):
        data = {
            "name": "Bad Drink",
            "category": "Test",
            "instructions": "Error expected.",
            "recipe_items": [
                {"ingredient": self.ingredient_1.id, "amount": 50, "unit": "ml"},
                {"ingredient": self.ingredient_1.id, "amount": 30, "unit": "ml"}
            ]
        }

        response = self.client.post(self.cocktail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_delete_ingredient_in_use_returns_conflict(self):
        cocktail = Cocktail.objects.create(
            name="Rum Shot",
            category="Shot",
            instructions="Drink!"
        )
        CocktailIngredient.objects.create(
            cocktail=cocktail,
            ingredient=self.ingredient_1,
            amount=40,
            unit="ml"
        )

        detail_url = reverse("ingredient-detail", kwargs={"pk": self.ingredient_1.id})
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Ingredient.objects.filter(id=self.ingredient_1.id).exists(), True)


    def test_filter_cocktails_by_category_and_alcohol(self):
        cocktail_1 = Cocktail.objects.create(name="Mojito", category="Long Drink", instructions="Muddle mint and lime.")
        CocktailIngredient.objects.create(cocktail=cocktail_1, ingredient=self.ingredient_1, amount=50, unit="ml")

        cocktail_2 = Cocktail.objects.create(name="Virgin Cola", category="Mocktail", instructions="Pour cola over ice.")
        CocktailIngredient.objects.create(cocktail=cocktail_2, ingredient=self.ingredient_2, amount=200, unit="ml")

        response = self.client.get(self.cocktail_url, {"category": "Long Drink"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mojito")

        response_non_alc = self.client.get(self.cocktail_url, {"is_alcoholic": "false"})
        self.assertEqual(response_non_alc.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_non_alc.data["results"]), 1)
        self.assertEqual(response_non_alc.data["results"][0]["name"], "Virgin Cola")