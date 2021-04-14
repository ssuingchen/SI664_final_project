from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from recipes.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from recipes.models import Recipe, RecipeData, Comment, Fav, Rate
from recipes.forms import RecipeCreateForm, RecipeTypeCreateForm, CommentForm, RateForm
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

# Create your views here.

class RecipeListView(View):
    model = Recipe
    template_name = "recipes/recipe_list.html"

    def get(self, request):
        recipe_list = Recipe.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_things.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        ctx = {'recipe_list': recipe_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)


class UserRecipeListView(LoginRequiredMixin, View):
    model = Recipe
    template_name = "recipes/user_recipe_list.html"

    def get(self, request):
        recipe_list = Recipe.objects.filter(owner=request.user)
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_things.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        ctx = {'recipe_list': recipe_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)



class RecipeDetailView(OwnerDetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    def get(self, request, pk) :
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_things.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        recipe = Recipe.objects.get(id=pk)
        comments = Comment.objects.filter(recipe=recipe).order_by('-updated_at')
        comment_form = CommentForm()
        rates = Rate.objects.filter(recipe=recipe).order_by('-updated_at')
        rate_form = RateForm()
        if Rate.objects.filter(recipe=recipe):
            total_ratings = Rate.objects.filter(recipe=recipe).aggregate(Sum('rate'))['rate__sum']
            num_rates = Rate.objects.filter(recipe=recipe).count()
            average_rate_per_recipe = total_ratings / num_rates
            context = { 'recipe' : recipe, 'comments': comments, 'comment_form': comment_form, 'average_rate_per_recipe':average_rate_per_recipe,
                        'rates':rates, 'rate_form':rate_form, 'favorites': favorites }
        else:
            context = { 'recipe' : recipe, 'comments': comments, 'comment_form': comment_form,'average_rate_per_recipe':'None',
                            'rates':rates, 'rate_form':rate_form, 'favorites': favorites }
        return render(request, self.template_name, context)


def recipe_generator(text):
    recipe_list = RecipeData.objects
    for ingredient in text.split(' '):
        recipe_list = recipe_list.filter(ingredients__contains=ingredient.lower())
    if recipe_list:
        return recipe_list[0]

    return None

class RecipeCreateView(LoginRequiredMixin, View):
    model = Recipe
    template_name = 'recipes/recipe_form.html'
    success_url = reverse_lazy('recipes:all')

    def get(self, request, pk=None):
        recipeTypeCreateForm = RecipeTypeCreateForm()
        recipeCreateForm = RecipeCreateForm()
        ctx = {'recipeCreateForm': recipeCreateForm, 'recipeTypeCreateForm':recipeTypeCreateForm}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        recipeTypeCreateForm = RecipeTypeCreateForm(request.POST)
        recipeCreateForm = RecipeCreateForm(request.POST)

        if not recipeTypeCreateForm.is_valid():
            ctx = {'recipeCreateForm': recipeCreateForm, 'recipeTypeCreateForm':recipeTypeCreateForm}
            return render(request, self.template_name, ctx)

        if not recipeCreateForm.is_valid():
            ctx = {'recipeCreateForm': recipeCreateForm, 'recipeTypeCreateForm':recipeTypeCreateForm}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        recipe_type = recipeTypeCreateForm.save(commit=True)
        recipe = recipeCreateForm.save(commit=False)
        recipe.dish = recipe_type
        recipe.owner = self.request.user
        found_object = recipe_generator(recipe.ingredients)
        if found_object:
            recipe.generated_text = found_object.instructions
            recipe.ingredients = found_object.ingredients
            recipe.title = found_object.title
        recipe.save()
        return redirect(self.success_url)


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ['ingredients', ]
    success_url = reverse_lazy('recipes:all')


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    fields = ['ingredients',]
    success_url = reverse_lazy('recipes:all')


class CommentCreateView(LoginRequiredMixin, View):
    model = Comment
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, recipe=recipe)
        comment.save()
        return redirect(reverse('recipes:recipe_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "recipes/comment_delete.html"
    success_url=reverse_lazy('recipes:recipe_detail')

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        recipe = self.object.recipe
        return reverse('recipes:recipe_detail', args=[recipe.id])


# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        recipe = get_object_or_404(Recipe, id=pk)
        fav = Fav(user=request.user, recipe=recipe)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, recipe=recipe).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()


class RateCreateView(LoginRequiredMixin, CreateView):
    model = Rate
    fields = '__all__'
    def post(self, request, pk) :
        recipe = get_object_or_404(Recipe, id=pk)
        rate = Rate(rate=request.POST['rate'], recipe=recipe)
        rate.save()
        return redirect(reverse('recipes:recipe_detail', args=[pk]))
