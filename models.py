from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings
from transformers import pipeline


class UserRecipe(models.Model):

    ingredients = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    recipe_length = models.IntegerField(
            validators=[MaxLengthValidator(30, "Recipe length must be lower than 30")]
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='recipe_owned')
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Comment', related_name='recipe_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self):
        self.generator = pipeline('text-generation', model='gpt2')
        self.generated_recipe = self.gpt2_generator()

    def gpt2_generator(self):
        ingredient_list = ['Place'+self.ingredients]
        while True:
            generated_recipe = self.generator(ingredient_list[-1], return_full_text = False, max_length=self.recipe_length, num_beams=5, no_repeat_ngram_size=2)
            ingredient_list.append(generated_recipe[0]['generated_text'])
            if len(ingredient_list) >= 10:
                break
        recipe_instruction = "".join(ingredient_list).replace(". ", ".\n")
        return recipe_instruction


class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )
    userRecipe = models.ForeignKey(UserRecipe, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'


# Reference:

# https://colab.research.google.com/github/huggingface/blog/blob/master/notebooks/02_how_to_generate.ipynb
# https://huggingface.co/transformers/task_summary.html#text-generation
# https://huggingface.co/transformers/main_classes/pipelines.html
# https://huggingface.co/transformers/main_classes/model.html#transformers.PreTrainedModel