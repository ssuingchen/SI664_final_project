from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.contrib.auth.models import User

# from transformers import pipeline
DISH_CHOICES= [
    ('salad', 'Salad'),
    ('entree', 'Entree'),
    ('dessert', 'Dessert'),
    ]

def validate_integer(value):
    if value < 5 or value > 30:
        raise ValidationError(
            gettext_lazy('%(value)s is out of range'),
            params={'value': value},
        )


class RecipeData(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.CharField(max_length=200)
    instructions = models.TextField()

    def __str__(self) :
        output = self.title + '\n' + self.ingredients + '\n' + self.instructions
        return output


def recipe_generator(text):
    recipe_list = RecipeData.objects
    for ingredient in text:
        recipe_list = recipe_list.filter(ingredients_icontain = ingredient)

    return recipe_list


class RecipeType(models.Model):
    recipe_type = models.CharField(max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")],
            choices=DISH_CHOICES, default='salad'
    )

    def __str__(self) :
        return self.recipe_type


class Recipe(models.Model):
    title = models.TextField(default='Empty')
    ingredients = models.TextField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    dish = models.ForeignKey(RecipeType,
        on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User,
        on_delete=models.CASCADE, related_name='recipe_owned')
    comments = models.ManyToManyField(User,
        through='Comment', related_name='recipe_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(User,
        through='Fav', related_name='favorite_things')
    generated_text = models.TextField(default='Empty')


class Comment(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

class Rate(models.Model):
    rate = models.IntegerField()
    # ratings = GenericRelation(Rating, related_query_name='rates')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self) :
        return 'Rating: %s'%(self.rate)

class Fav(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='favs_users')

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.recipe.title[:10])



# Reference:

# https://colab.research.google.com/github/huggingface/blog/blob/master/notebooks/02_how_to_generate.ipynb
# https://huggingface.co/transformers/task_summary.html#text-generation
# https://huggingface.co/transformers/main_classes/pipelines.html
# https://huggingface.co/transformers/main_classes/model.html#transformers.PreTrainedModel