from django import forms
from recipes.models import Recipe, RecipeType

INTEGER_CHOICES= [tuple([x,x]) for x in range(1,6)]


class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['ingredients']


class RecipeTypeCreateForm(forms.ModelForm):
    class Meta:
        model = RecipeType
        fields = '__all__'


# strip means to remove whitespace from the beginning and the end before storing the column
class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)

class RateForm(forms.Form):
    rate = forms.IntegerField(required=True, widget=forms.Select(choices=INTEGER_CHOICES))

# https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/3.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
