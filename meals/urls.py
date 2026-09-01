from django.urls import path

from . import views

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("recipes/new/", views.recipe_form, name="recipe_new"),
    path("recipes/<int:pk>/edit/", views.recipe_form, name="recipe_edit"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    path("shopping-list/", views.shopping_list, name="shopping_list"),
    path("clear-plan/", views.clear_plan, name="clear_plan"),
]
