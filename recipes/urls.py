from django.urls import path, reverse_lazy
from . import views

app_name='recipes'
urlpatterns = [
    path('', views.RecipeListView.as_view(), name='all'),
    path('user/', views.UserRecipeListView.as_view(), name='user_page'),
    path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/create',
        views.RecipeCreateView.as_view(success_url=reverse_lazy('recipes:all')), name='recipe_create'),
    path('recipe/<int:pk>/update/', views.RecipeUpdateView.as_view(), name='recipe_update'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('recipe/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='recipe_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(), name='recipe_comment_delete'),
    path('recipe/<int:pk>/favorite',
        views.AddFavoriteView.as_view(), name='recipe_favorite'),
    path('recipe/<int:pk>/unfavorite',
        views.DeleteFavoriteView.as_view(), name='recipe_unfavorite'),
    path('recipe/<int:pk>/rate',
        views.RateCreateView.as_view(), name='recipe_rate_create'),
]