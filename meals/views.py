from datetime import date, timedelta

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .aggregation import aggregate
from .models import Ingredient, PlanEntry, Recipe, Unit


def recipe_list(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist("recipes")
        PlanEntry.objects.exclude(recipe_id__in=selected_ids).delete()
        for recipe_id in selected_ids:
            PlanEntry.objects.get_or_create(recipe_id=recipe_id)
        if "show_list" in request.POST:
            return redirect("shopping_list")
        messages.success(request, "Meal plan saved.")
        return redirect("recipe_list")

    recipes = Recipe.objects.prefetch_related("ingredients").all()
    planned_ids = set(PlanEntry.objects.values_list("recipe_id", flat=True))
    today = date.today()
    week = [today + timedelta(days=i) for i in range(7)]
    return render(
        request,
        "meals/recipe_list.html",
        {"recipes": recipes, "planned_ids": planned_ids, "week": week},
    )


def _parse_recipe_form(post):
    """Validate the hand-rolled recipe form. Returns (data, rows, errors)."""
    errors = []

    name = post.get("name", "").strip()
    if not name:
        errors.append("Give the recipe a name.")

    servings = post.get("servings", "").strip()
    if servings:
        try:
            servings = int(servings)
            if servings < 1:
                raise ValueError
        except ValueError:
            errors.append("Servings must be a positive number.")
            servings = None
    else:
        servings = None

    valid_units = {u.value for u in Unit}
    rows = []
    for ing_name, ing_qty, ing_unit in zip(
        post.getlist("ing_name"), post.getlist("ing_qty"), post.getlist("ing_unit")
    ):
        ing_name = ing_name.strip()
        ing_qty = ing_qty.strip().replace(",", ".")
        if not ing_name and not ing_qty:
            continue  # untouched empty row

        row = {"name": ing_name, "qty": ing_qty, "unit": ing_unit}
        rows.append(row)
        if not ing_name:
            errors.append("An ingredient row is missing a name.")
            continue
        try:
            qty = float(ing_qty)
            if qty <= 0:
                raise ValueError
        except ValueError:
            errors.append(f'"{ing_name}" needs a quantity greater than zero.')
            continue
        if ing_unit not in valid_units:
            errors.append(f'"{ing_name}" needs a unit.')
            continue
        row["qty_value"] = qty

    if not rows:
        errors.append("Add at least one ingredient.")

    data = {
        "name": name,
        "servings": servings,
        "instructions": post.get("instructions", "").strip(),
    }
    return data, rows, errors


def recipe_form(request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk) if pk else None

    if request.method == "POST":
        data, rows, errors = _parse_recipe_form(request.POST)
        if not errors:
            with transaction.atomic():
                if recipe is None:
                    recipe = Recipe.objects.create(**data)
                else:
                    for field, value in data.items():
                        setattr(recipe, field, value)
                    recipe.save()
                    recipe.ingredients.all().delete()
                Ingredient.objects.bulk_create(
                    Ingredient(
                        recipe=recipe,
                        name=row["name"],
                        quantity=row["qty_value"],
                        unit=row["unit"],
                    )
                    for row in rows
                )
            messages.success(request, f'Saved "{recipe.name}".')
            return redirect("recipe_list")
        form = {**data, "servings": request.POST.get("servings", "")}
    else:
        errors = []
        if recipe:
            form = {
                "name": recipe.name,
                "servings": recipe.servings or "",
                "instructions": recipe.instructions,
            }
            rows = [
                {
                    "name": ing.name,
                    "qty": f"{ing.quantity:g}",
                    "unit": ing.unit,
                }
                for ing in recipe.ingredients.all()
            ]
        else:
            form = {"name": "", "servings": "", "instructions": ""}
            rows = [{"name": "", "qty": "", "unit": ""}] * 3

    return render(
        request,
        "meals/recipe_form.html",
        {
            "recipe": recipe,
            "form": form,
            "rows": rows,
            "errors": errors,
            "units": Unit.values,
        },
    )


@require_POST
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    name = recipe.name
    recipe.delete()
    messages.success(request, f'Deleted "{name}".')
    return redirect("recipe_list")


def shopping_list(request):
    planned_recipes = Recipe.objects.filter(plan_entry__isnull=False)
    ingredients = Ingredient.objects.filter(
        recipe__in=planned_recipes
    ).select_related("recipe")
    return render(
        request,
        "meals/shopping_list.html",
        {"lines": aggregate(ingredients), "planned_recipes": planned_recipes},
    )


@require_POST
def clear_plan(request):
    PlanEntry.objects.all().delete()
    return redirect("recipe_list")
