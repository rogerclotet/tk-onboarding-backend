import json

from rest_framework.test import APITestCase
from recipes.models import Recipe, Ingredient
from django.contrib.auth.models import User, Permission, ContentType


class RecipesTestCase(APITestCase):
    user = None

    def setUp(self) -> None:
        self.user = User.objects.create_user("test")
        ct = ContentType.objects.get_for_model(Recipe)
        permissions = ["add_recipe", "change_recipe", "delete_recipe"]
        for codename in permissions:
            permission = Permission.objects.get(content_type=ct, codename=codename)
            self.user.user_permissions.add(permission)

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

    def test_recipe_list(self):
        first_recipe = Recipe.objects.create(
            name="First recipe", description="First description"
        )
        Ingredient.objects.create(name="First recipe ingredient 1", recipe=first_recipe)
        Ingredient.objects.create(name="First recipe ingredient 2", recipe=first_recipe)

        second_recipe = Recipe.objects.create(
            name="Second recipe", description="Second description"
        )
        Ingredient.objects.create(
            name="Second recipe ingredient 1", recipe=second_recipe
        )
        Ingredient.objects.create(
            name="Second recipe ingredient 2", recipe=second_recipe
        )
        Ingredient.objects.create(
            name="Second recipe ingredient 3", recipe=second_recipe
        )

        response = self.client.get("/recipes/")

        self.assertEquals(response.status_code, 200)

        recipes = response.json()

        self.assertEquals(len(recipes), 2)

        self.assertEquals(recipes[0]["name"], "First recipe")
        self.assertEquals(recipes[0]["description"], "First description")
        self.assertEquals(len(recipes[0]["ingredients"]), 2)
        self.assertEquals(
            recipes[0]["ingredients"][0]["name"], "First recipe ingredient 1"
        )
        self.assertEquals(
            recipes[0]["ingredients"][1]["name"], "First recipe ingredient 2"
        )

        self.assertEquals(recipes[1]["name"], "Second recipe")
        self.assertEquals(recipes[1]["description"], "Second description")
        self.assertEquals(len(recipes[1]["ingredients"]), 3)
        self.assertEquals(
            recipes[1]["ingredients"][0]["name"], "Second recipe ingredient 1"
        )
        self.assertEquals(
            recipes[1]["ingredients"][1]["name"], "Second recipe ingredient 2"
        )
        self.assertEquals(
            recipes[1]["ingredients"][2]["name"], "Second recipe ingredient 3"
        )

    def test_recipe_create(self):
        self.client.force_login(user=self.user)

        response = self.client.post(
            "/recipes/",
            {
                "name": "New recipe",
                "description": "New description",
                "ingredients": [
                    {"name": "First ingredient"},
                    {"name": "Second ingredient"},
                ],
            },
            format="json",
        )

        self.assertEquals(response.status_code, 201)

        new_recipe_id = response.json()["id"]

        new_recipe = Recipe.objects.get(id=new_recipe_id)

        self.assertEquals(new_recipe.id, new_recipe_id)
        self.assertEquals(new_recipe.name, "New recipe")
        self.assertEquals(new_recipe.description, "New description")
        ingredients = new_recipe.ingredients.values()
        self.assertEquals(len(ingredients), 2)
        self.assertEquals(ingredients[0]["name"], "First ingredient")
        self.assertEquals(ingredients[1]["name"], "Second ingredient")

    def test_recipe_update(self):
        self.client.force_login(user=self.user)

        recipe = Recipe.objects.create(
            name="Initial name", description="Initial description"
        )
        for ingredient_name in ["First ingredient", "Second ingredient"]:
            Ingredient.objects.create(name=ingredient_name, recipe=recipe)

        response = self.client.patch(
            f"/recipes/{recipe.id}/", {"name": "Edited name"}, format="json"
        )
        self.assertEquals(response.status_code, 200)
        updated_recipe = Recipe.objects.get(id=recipe.id)
        self.assertEquals(updated_recipe.name, "Edited name")

        self.client.patch(
            f"/recipes/{recipe.id}/",
            {"description": "Edited description"},
            format="json",
        )
        self.assertEquals(response.status_code, 200)
        updated_recipe = Recipe.objects.get(id=recipe.id)
        self.assertEquals(updated_recipe.description, "Edited description")

        self.client.patch(
            f"/recipes/{recipe.id}/",
            {
                "ingredients": [
                    {"name": "Third ingredient"},
                    {"name": "Fourth ingredient"},
                ]
            },
            format="json",
        )
        self.assertEquals(response.status_code, 200)
        updated_recipe = Recipe.objects.get(id=recipe.id)
        ingredients = updated_recipe.ingredients.values()
        self.assertEquals(len(ingredients), 2)
        self.assertEquals(ingredients[0]["name"], "Third ingredient")
        self.assertEquals(ingredients[1]["name"], "Fourth ingredient")

    def test_delete_recipe(self):
        self.client.force_login(user=self.user)

        recipe = Recipe.objects.create(name="Name", description="Description")
        for ingredient_name in ["First ingredient", "Second ingredient"]:
            Ingredient.objects.create(name=ingredient_name, recipe=recipe)

        recipe_id = recipe.id
        response = self.client.delete(f"/recipes/{recipe_id}/")

        self.assertEquals(response.status_code, 204)

        self.assertEquals(Recipe.objects.filter(id=recipe_id).count(), 0)
        self.assertEquals(Ingredient.objects.filter(recipe_id=recipe_id).count(), 0)
