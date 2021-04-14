import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load

from recipes.models import RecipeData


def run():
    fhand = open('recipes/recipe.csv')
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    RecipeData.objects.all().delete()

    # Format
    # title,ingredients,instructions

    for row in reader:
        print(row)
        recipeData = RecipeData(title = row[1], ingredients = row[2], instructions = row[3])
        recipeData.save()