from django.contrib import admin

from .models import Ingredient, PlanEntry, Recipe


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "servings", "ingredient_count", "created_at"]
    search_fields = ["name", "ingredients__name"]
    inlines = [IngredientInline]

    @admin.display(description="Ingredients")
    def ingredient_count(self, obj):
        return obj.ingredients.count()


@admin.register(PlanEntry)
class PlanEntryAdmin(admin.ModelAdmin):
    list_display = ["recipe"]
