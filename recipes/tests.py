import json

from django.test import TestCase

from recipes.models import Recipe, Ingredient


class RecipesTestCase(TestCase):
    def test_recipe_detail(self):
        name = "Test recipe"
        description = "Test description"
        ingredients = ["First ingredient", "Second ingredient"]

        recipe = Recipe.objects.create(name=name, description=description)
        for ingredient_name in ingredients:
            Ingredient.objects.create(name=ingredient_name, recipe=recipe)

        response = self.client.get(f"/recipes/{recipe.id}/")

        self.assertEquals(response.status_code, 200)

        response_recipe = response.json()

        self.assertEquals(response_recipe["name"], name)
        self.assertEquals(response_recipe["description"], description)

        recipe_ingredients = response_recipe["ingredients"]
        self.assertEquals(len(recipe_ingredients), 2)
        for recipe_ingredient in recipe_ingredients:
            self.assertIn(recipe_ingredient["name"], ingredients)
