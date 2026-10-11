from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .aggregation import aggregate
from .models import CookingDay, Ingredient, Recipe


class AggregationTests(SimpleTestCase):
    def test_same_unit_stacks(self):
        lines = aggregate(
            [
                ("Butter", 200, "g", "Carbonara"),
                ("Butter", 300, "g", "Cookies"),
            ]
        )
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].quantity, 500)
        self.assertEqual(lines[0].unit, "g")
        self.assertEqual(lines[0].recipes, ["Carbonara", "Cookies"])
        self.assertEqual(lines[0].display_quantity, "500 g")

    def test_kg_and_g_stack(self):
        lines = aggregate(
            [
                ("Flour", 1, "kg", "Bread"),
                ("Flour", 300, "g", "Pancakes"),
            ]
        )
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].quantity, 1300)
        self.assertEqual(lines[0].unit, "g")
        self.assertEqual(lines[0].display_quantity, "1.3 kg")

    def test_l_and_ml_stack(self):
        lines = aggregate(
            [
                ("Milk", 0.5, "l", "Pancakes"),
                ("Milk", 250, "ml", "Sauce"),
            ]
        )
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].quantity, 750)
        self.assertEqual(lines[0].display_quantity, "750 ml")

    def test_incompatible_units_stay_separate(self):
        lines = aggregate(
            [
                ("Flour", 200, "g", "Bread"),
                ("Flour", 1, "cup", "Cookies"),
            ]
        )
        self.assertEqual(len(lines), 2)
        units = sorted(line.unit for line in lines)
        self.assertEqual(units, ["cup", "g"])

    def test_name_matching_ignores_case_and_whitespace(self):
        lines = aggregate(
            [
                ("Olive Oil", 30, "ml", "Salad"),
                ("  olive oil ", 20, "ml", "Pasta"),
            ]
        )
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].name, "Olive Oil")  # first-seen casing
        self.assertEqual(lines[0].quantity, 50)

    def test_display_trims_trailing_zeros(self):
        lines = aggregate([("Sugar", 1500, "g", "Cake")])
        self.assertEqual(lines[0].display_quantity, "1.5 kg")
        lines = aggregate([("Eggs", 4, "pcs", "Omelette")])
        self.assertEqual(lines[0].display_quantity, "4 pcs")
        lines = aggregate([("Milk", 1250, "ml", "Pancakes")])
        self.assertEqual(lines[0].display_quantity, "1.25 l")

    def test_exactly_threshold_displays_bigger_unit(self):
        lines = aggregate([("Water", 1, "l", "Soup")])
        self.assertEqual(lines[0].display_quantity, "1 l")

    def test_sorted_alphabetically(self):
        lines = aggregate(
            [
                ("Zucchini", 2, "pcs", "Stir Fry"),
                ("Apple", 3, "pcs", "Pie"),
            ]
        )
        self.assertEqual([line.name for line in lines], ["Apple", "Zucchini"])

    def test_recipe_listed_once_per_line(self):
        lines = aggregate(
            [
                ("Salt", 1, "pinch", "Soup"),
                ("Salt", 2, "pinch", "Soup"),
            ]
        )
        self.assertEqual(lines[0].recipes, ["Soup"])
        self.assertEqual(lines[0].quantity, 3)


class RecipeFormViewTests(TestCase):
    def test_create_recipe(self):
        response = self.client.post(
            reverse("recipe_new"),
            {
                "name": "Toast",
                "servings": "1",
                "instructions": "Toast the bread.",
                "ing_name": ["Bread", "Butter", ""],
                "ing_qty": ["2", "10", ""],
                "ing_unit": ["pcs", "g", ""],
            },
        )
        self.assertRedirects(response, reverse("recipe_list"))
        recipe = Recipe.objects.get(name="Toast")
        self.assertEqual(recipe.servings, 1)
        self.assertEqual(recipe.ingredients.count(), 2)  # empty row skipped

    def test_create_rejects_missing_name_and_bad_qty(self):
        response = self.client.post(
            reverse("recipe_new"),
            {
                "name": "",
                "servings": "",
                "instructions": "",
                "ing_name": ["Bread"],
                "ing_qty": ["-5"],
                "ing_unit": ["pcs"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["errors"])
        self.assertEqual(Recipe.objects.count(), 0)

    def test_comma_decimal_quantity_accepted(self):
        self.client.post(
            reverse("recipe_new"),
            {
                "name": "Dough",
                "servings": "",
                "instructions": "",
                "ing_name": ["Yeast"],
                "ing_qty": ["1,5"],
                "ing_unit": ["tsp"],
            },
        )
        self.assertEqual(Recipe.objects.get(name="Dough").ingredients.first().quantity, 1.5)

    def test_edit_replaces_ingredients(self):
        recipe = Recipe.objects.create(name="Soup")
        Ingredient.objects.create(recipe=recipe, name="Water", quantity=1, unit="l")
        response = self.client.post(
            reverse("recipe_edit", args=[recipe.pk]),
            {
                "name": "Better Soup",
                "servings": "",
                "instructions": "",
                "ing_name": ["Broth"],
                "ing_qty": ["750"],
                "ing_unit": ["ml"],
            },
        )
        self.assertRedirects(response, reverse("recipe_list"))
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Better Soup")
        self.assertEqual(
            list(recipe.ingredients.values_list("name", flat=True)), ["Broth"]
        )

    def test_delete_recipe(self):
        recipe = Recipe.objects.create(name="Old")
        response = self.client.post(reverse("recipe_delete", args=[recipe.pk]))
        self.assertRedirects(response, reverse("recipe_list"))
        self.assertEqual(Recipe.objects.count(), 0)


class CookingDayTests(TestCase):
    def test_toggle_marks_a_day(self):
        today = date.today()
        response = self.client.post(
            reverse("toggle_cooking_day"), {"date": today.isoformat()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"marked": True})
        self.assertTrue(CookingDay.objects.filter(date=today).exists())

    def test_toggle_unmarks_a_marked_day(self):
        today = date.today()
        CookingDay.objects.create(date=today)
        response = self.client.post(
            reverse("toggle_cooking_day"), {"date": today.isoformat()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"marked": False})
        self.assertFalse(CookingDay.objects.filter(date=today).exists())

    def test_toggle_rejects_invalid_date(self):
        response = self.client.post(
            reverse("toggle_cooking_day"), {"date": "not-a-date"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CookingDay.objects.count(), 0)

    def test_toggle_rejects_date_outside_rolling_week(self):
        today = date.today()
        for day in (today - timedelta(days=1), today + timedelta(days=7)):
            response = self.client.post(
                reverse("toggle_cooking_day"), {"date": day.isoformat()}
            )
            self.assertEqual(response.status_code, 400)
        self.assertEqual(CookingDay.objects.count(), 0)

    def test_planning_page_prunes_past_cooking_days(self):
        today = date.today()
        CookingDay.objects.create(date=today - timedelta(days=1))
        CookingDay.objects.create(date=today)
        self.client.get(reverse("recipe_list"))
        self.assertEqual(
            list(CookingDay.objects.values_list("date", flat=True)), [today]
        )

    def test_planning_page_renders_marked_day(self):
        today = date.today()
        CookingDay.objects.create(date=today)
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(
            response,
            f'class="day-pill today marked" data-key="{today.isoformat()}"',
        )
