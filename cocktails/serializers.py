from rest_framework import serializers
from .models import Cocktail, CocktailIngredient, Ingredient
from django.contrib.auth.models import User

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ["id", "name", "description", "is_alcoholic", "image_url"]


class CocktailIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(
        source="ingredient.name",
        read_only=True
    )

    class Meta:
        model = CocktailIngredient
        fields = ["ingredient", "ingredient_name", "amount", "unit"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")

        return value


class CocktailSerializer(serializers.ModelSerializer):
    recipe_items = CocktailIngredientSerializer(many=True)

    class Meta:
        model = Cocktail
        fields = ["id", "name", "category", "instructions", "recipe_items", "created_at"]

    def validate_recipe_items(self, items):
        if not items:
            raise serializers.ValidationError("Minimum one ingredient required to create Cocktail.")

        ingredient_ids = [item["ingredient"].pk for item in items]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ingredients must be unique.")

        return items

    def save_items(self, cocktail, items):
        CocktailIngredient.objects.bulk_create(
            [CocktailIngredient(cocktail=cocktail, **item) for item in items]
        )

    def create(self, validated_data):
        request = self.context.get("request")

        if request and request.user and request.user.is_authenticated:
            validated_data["author"] = request.user

        items = validated_data.pop("recipe_items")
        cocktail = Cocktail.objects.create(**validated_data)
        self.save_items(cocktail, items)

        return cocktail

    def update(self, instance, validated_data):
        items = validated_data.pop("recipe_items", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if items is not None:
            instance.recipe_items.all().delete()
            self.save_items(instance, items)

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )
        return user