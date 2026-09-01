"""One-off seed script: creates example recipes if the database is empty.

Run with: python manage.py shell -c "import seed"
"""

from meals.models import Ingredient, Recipe

if Recipe.objects.exists():
    print("Recipes already exist, skipping seed.")
else:
    carbonara = Recipe.objects.create(
        name="Spaghetti Carbonara",
        servings=2,
        instructions=(
            "Boil spaghetti. Fry pancetta. Mix eggs with grated cheese, "
            "combine off heat with pasta and pancetta."
        ),
    )
    Ingredient.objects.bulk_create(
        [
            Ingredient(recipe=carbonara, name="Spaghetti", quantity=200, unit="g"),
            Ingredient(recipe=carbonara, name="Pancetta", quantity=100, unit="g"),
            Ingredient(recipe=carbonara, name="Eggs", quantity=2, unit="pcs"),
            Ingredient(recipe=carbonara, name="Parmesan", quantity=50, unit="g"),
            Ingredient(recipe=carbonara, name="Black pepper", quantity=1, unit="pinch"),
        ]
    )

    pancakes = Recipe.objects.create(
        name="Pancakes",
        servings=2,
        instructions="Whisk everything into a batter, fry on a buttered pan.",
    )
    Ingredient.objects.bulk_create(
        [
            Ingredient(recipe=pancakes, name="Flour", quantity=250, unit="g"),
            Ingredient(recipe=pancakes, name="Milk", quantity=500, unit="ml"),
            Ingredient(recipe=pancakes, name="Eggs", quantity=2, unit="pcs"),
            Ingredient(recipe=pancakes, name="Butter", quantity=30, unit="g"),
            Ingredient(recipe=pancakes, name="Sugar", quantity=2, unit="tbsp"),
        ]
    )

    omelette = Recipe.objects.create(
        name="Cheese Omelette",
        servings=1,
        instructions="Beat eggs, pour into pan, add cheese, fold.",
    )
    Ingredient.objects.bulk_create(
        [
            Ingredient(recipe=omelette, name="Eggs", quantity=3, unit="pcs"),
            Ingredient(recipe=omelette, name="Butter", quantity=20, unit="g"),
            Ingredient(recipe=omelette, name="Cheese", quantity=60, unit="g"),
            Ingredient(recipe=omelette, name="Milk", quantity=50, unit="ml"),
        ]
    )

    print("Seeded 3 example recipes.")
