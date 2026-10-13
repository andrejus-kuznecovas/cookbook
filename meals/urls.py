from django.urls import path

from . import views

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("recipes/new/", views.recipe_form, name="recipe_new"),
    path("recipes/<int:pk>/edit/", views.recipe_form, name="recipe_edit"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    path("recipes/reorder/", views.reorder_recipes, name="reorder_recipes"),
    path("shopping-list/", views.shopping_list, name="shopping_list"),
    path("shopping-list/extras/add/", views.add_extra, name="add_extra"),
    path(
        "shopping-list/extras/<int:pk>/remove/",
        views.remove_extra,
        name="remove_extra",
    ),
    path(
        "shopping-list/barbora/add/",
        views.add_barbora_link,
        name="add_barbora_link",
    ),
    path(
        "settings/barbora/<int:pk>/remove/",
        views.remove_barbora_link,
        name="remove_barbora_link",
    ),
    path("settings/", views.user_settings, name="settings"),
    path("settings/staples/add/", views.add_staple, name="add_staple"),
    path(
        "settings/staples/<int:pk>/remove/",
        views.remove_staple,
        name="remove_staple",
    ),
    path("clear-plan/", views.clear_plan, name="clear_plan"),
    path(
        "cooking-days/toggle/",
        views.toggle_cooking_day,
        name="toggle_cooking_day",
    ),
]
