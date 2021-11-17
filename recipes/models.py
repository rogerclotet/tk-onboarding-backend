from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    recipe = models.ForeignKey(
        to=Recipe, related_name="ingredients", on_delete=models.CASCADE
    )
