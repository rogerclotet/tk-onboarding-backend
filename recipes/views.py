from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
