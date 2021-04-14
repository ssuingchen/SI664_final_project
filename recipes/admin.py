from django.contrib import admin
from recipes.models import Recipe, Comment, Fav, RecipeData
# Register your models here.
admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(Fav)
admin.site.register(RecipeData)