import json
from datetime import date, timedelta
from importlib import import_module

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .aggregation import aggregate, split_staples
from .models import (
    CookingDay,
    Extra,
    Ingredient,
    PlanEntry,
    Recipe,
    Staple,
    UserSetting,
)


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


class SplitStaplesTests(SimpleTestCase):
    """split_staples: partition aggregated lines into to-buy and assumed."""

    def lines(self, *rows):
        return aggregate(list(rows))

    def test_staple_lines_skipped_case_insensitively(self):
        lines = self.lines(
            ("Salt", 1, "pinch", "Soup"),
            ("Butter", 200, "g", "Cookies"),
        )
        to_buy, assumed = split_staples(lines, ["SALT"])
        self.assertEqual([line.name for line in to_buy], ["Butter"])
        self.assertEqual(assumed, ["Salt"])

    def test_staple_skips_every_unit_variant_of_the_name(self):
        # Incompatible units keep Flour on two lines; the staple hides both.
        lines = self.lines(
            ("Flour", 200, "g", "Bread"),
            ("Flour", 1, "cup", "Cookies"),
            ("Milk", 1, "l", "Pancakes"),
        )
        to_buy, assumed = split_staples(lines, ["flour"])
        self.assertEqual([line.name for line in to_buy], ["Milk"])
        self.assertEqual(assumed, ["Flour"])  # disclosed once, not twice

    def test_empty_staples_leaves_lines_unchanged(self):
        lines = self.lines(
            ("Salt", 1, "pinch", "Soup"),
            ("Butter", 200, "g", "Cookies"),
        )
        to_buy, assumed = split_staples(lines, [])
        self.assertEqual(to_buy, lines)
        self.assertEqual(assumed, [])

    def test_unmatched_staples_are_not_disclosed(self):
        lines = self.lines(("Butter", 200, "g", "Cookies"))
        to_buy, assumed = split_staples(lines, ["saffron"])
        self.assertEqual([line.name for line in to_buy], ["Butter"])
        self.assertEqual(assumed, [])

    def test_staple_names_are_normalized_before_matching(self):
        lines = self.lines(("Olive Oil", 30, "ml", "Salad"))
        to_buy, assumed = split_staples(lines, ["  olive OIL  "])
        self.assertEqual(to_buy, [])
        self.assertEqual(assumed, ["Olive Oil"])  # line casing, not staple's

    def test_assumed_names_sorted_alphabetically(self):
        lines = self.lines(
            ("salt", 1, "pinch", "Soup"),
            ("Olive Oil", 30, "ml", "Salad"),
        )
        _, assumed = split_staples(lines, ["salt", "olive oil"])
        self.assertEqual(assumed, ["Olive Oil", "salt"])


class AuthTests(TestCase):
    """Every meals URL requires login; login and logout flows work."""

    LOGIN_URL = "/accounts/login/"

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.recipe = Recipe.objects.create(name="Soup")

    def anonymous_urls(self):
        """Every URL in meals/urls.py with the methods it accepts."""
        return [
            (reverse("recipe_list"), ["get", "post"]),
            (reverse("recipe_new"), ["get", "post"]),
            (reverse("recipe_edit", args=[self.recipe.pk]), ["get", "post"]),
            (reverse("recipe_delete", args=[self.recipe.pk]), ["get", "post"]),
            (reverse("reorder_recipes"), ["get", "post"]),
            (reverse("shopping_list"), ["get", "post"]),
            (reverse("add_extra"), ["get", "post"]),
            (reverse("remove_extra", args=[1]), ["get", "post"]),
            (reverse("clear_plan"), ["get", "post"]),
            (reverse("add_staple"), ["get", "post"]),
            (reverse("remove_staple", args=[1]), ["get", "post"]),
            (reverse("toggle_cooking_day"), ["get", "post"]),
            (reverse("settings"), ["get", "post"]),
        ]

    def test_anonymous_requests_redirect_to_login_with_next(self):
        for path, methods in self.anonymous_urls():
            for method in methods:
                with self.subTest(path=path, method=method):
                    response = getattr(self.client, method)(path)
                    self.assertRedirects(
                        response, f"{self.LOGIN_URL}?next={path}"
                    )

    def test_login_page_renders_for_anonymous(self):
        response = self.client.get(self.LOGIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_planning_page_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("recipe_list"))
        self.assertEqual(response.status_code, 200)

    def test_logout_post_logs_out_and_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, self.LOGIN_URL)
        # The session is gone: the planning page redirects to login again.
        response = self.client.get(reverse("recipe_list"))
        self.assertRedirects(response, f"{self.LOGIN_URL}?next=/")


class RecipeFormViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

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
    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

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

    def test_planning_page_renders_cooking_day(self):
        today = date.today()
        CookingDay.objects.create(date=today)
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(
            response,
            f'class="day-pill today marked" data-key="{today.isoformat()}"',
        )


class PlanningPageSearchTests(TestCase):
    """The planning page server-renders the search input and Surprise me control."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

    def test_planning_page_renders_search_and_surprise_controls(self):
        Recipe.objects.create(name="Soup")
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(response, 'id="recipe-search"')
        self.assertContains(response, 'id="search-clear"')
        self.assertContains(response, 'id="surprise-btn"')
        self.assertContains(response, "Surprise me")
        self.assertContains(response, "No recipes match")

    def test_empty_state_has_no_search_or_surprise_controls(self):
        response = self.client.get(reverse("recipe_list"))
        self.assertNotContains(response, 'id="recipe-search"')
        self.assertNotContains(response, 'id="surprise-btn"')


class ExtraTests(TestCase):
    """Extras: off-plan shared shopping lines (see GLOSSARY.md)."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

    def test_add_extra_and_redirect_back(self):
        response = self.client.post(reverse("add_extra"), {"name": "Dish soap"})
        self.assertRedirects(response, reverse("shopping_list"))
        self.assertEqual(
            list(Extra.objects.values_list("name", flat=True)), ["Dish soap"]
        )

    def test_add_strips_surrounding_whitespace(self):
        self.client.post(reverse("add_extra"), {"name": "  Coffee beans  "})
        self.assertEqual(Extra.objects.get().name, "Coffee beans")

    def test_add_rejects_empty_and_whitespace_names_silently(self):
        for name in ("", "   "):
            with self.subTest(name=repr(name)):
                response = self.client.post(reverse("add_extra"), {"name": name})
                self.assertRedirects(response, reverse("shopping_list"))
        self.assertEqual(Extra.objects.count(), 0)

    def test_remove_extra(self):
        extra = Extra.objects.create(name="Coffee beans")
        response = self.client.post(reverse("remove_extra", args=[extra.pk]))
        self.assertRedirects(response, reverse("shopping_list"))
        self.assertEqual(Extra.objects.count(), 0)

    def test_clear_plan_wipes_extras(self):
        recipe = Recipe.objects.create(name="Soup")
        PlanEntry.objects.create(recipe=recipe)
        Extra.objects.create(name="Dish soap")
        response = self.client.post(reverse("clear_plan"))
        self.assertRedirects(response, reverse("recipe_list"))
        self.assertEqual(PlanEntry.objects.count(), 0)
        self.assertEqual(Extra.objects.count(), 0)

    def test_extras_visible_to_another_authenticated_user(self):
        extra = Extra.objects.create(name="Dish soap")
        other = User.objects.create_user("other-partner", password="test-pass-456")
        self.client.force_login(other)
        response = self.client.get(reverse("shopping_list"))
        self.assertContains(response, "Dish soap")
        self.assertContains(response, f'data-key="extra|{extra.pk}"')

    def test_extras_section_and_form_show_without_planned_meals(self):
        response = self.client.get(reverse("shopping_list"))
        self.assertContains(response, "Extras")
        self.assertContains(response, f'action="{reverse("add_extra")}"')
        # The empty state still appears when no meals are selected.
        self.assertContains(response, "No meals selected yet")


class StapleTests(TestCase):
    """Staples: shared always-at-home ingredient names (see GLOSSARY.md)."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

    def plan_recipe_with(self, *ingredient_rows):
        recipe = Recipe.objects.create(name="Soup")
        for name, quantity, unit in ingredient_rows:
            Ingredient.objects.create(
                recipe=recipe, name=name, quantity=quantity, unit=unit
            )
        PlanEntry.objects.create(recipe=recipe)
        return recipe

    # ----- add / remove views -----

    def test_add_staple_and_redirect_to_settings(self):
        response = self.client.post(reverse("add_staple"), {"name": "Salt"})
        self.assertRedirects(response, reverse("settings"))
        self.assertEqual(
            list(Staple.objects.values_list("name", flat=True)), ["Salt"]
        )

    def test_add_strips_surrounding_whitespace(self):
        self.client.post(reverse("add_staple"), {"name": "  Olive oil  "})
        self.assertEqual(Staple.objects.get().name, "Olive oil")

    def test_add_rejects_empty_and_whitespace_names_silently(self):
        for name in ("", "   "):
            with self.subTest(name=repr(name)):
                response = self.client.post(reverse("add_staple"), {"name": name})
                self.assertRedirects(response, reverse("settings"))
        self.assertEqual(Staple.objects.count(), 0)

    def test_duplicate_add_is_a_silent_noop_case_insensitively(self):
        Staple.objects.create(name="Salt")
        for name in ("Salt", "salt", "  SALT "):
            with self.subTest(name=name):
                response = self.client.post(
                    reverse("add_staple"), {"name": name}, follow=True
                )
                self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(Staple.objects.values_list("name", flat=True)), ["Salt"]
        )

    def test_remove_staple(self):
        staple = Staple.objects.create(name="Salt")
        response = self.client.post(reverse("remove_staple", args=[staple.pk]))
        self.assertRedirects(response, reverse("settings"))
        self.assertEqual(Staple.objects.count(), 0)

    # ----- Settings page -----

    def test_settings_page_lists_staples_with_remove_and_add_controls(self):
        staple = Staple.objects.create(name="Olive oil")
        response = self.client.get(reverse("settings"))
        self.assertContains(response, "Olive oil")
        self.assertContains(
            response, f'action="{reverse("remove_staple", args=[staple.pk])}"'
        )
        self.assertContains(response, f'action="{reverse("add_staple")}"')

    def test_staples_shared_with_the_other_partner(self):
        Staple.objects.create(name="Pepper")
        other = User.objects.create_user("other-partner", password="test-pass-456")
        self.client.force_login(other)
        response = self.client.get(reverse("settings"))
        self.assertContains(response, "Pepper")

    # ----- Shopping List filtering and disclosure -----

    def test_shopping_list_excludes_staples_and_discloses_them(self):
        self.plan_recipe_with(("Salt", 1, "pinch"), ("Butter", 200, "g"))
        Staple.objects.create(name="salt")
        response = self.client.get(reverse("shopping_list"))
        self.assertNotContains(response, 'item-name">Salt')
        self.assertContains(response, 'item-name">Butter')
        self.assertContains(response, "Assumed you have")
        self.assertContains(response, "Salt")

    def test_shopping_list_without_staples_has_no_disclosure(self):
        self.plan_recipe_with(("Salt", 1, "pinch"))
        response = self.client.get(reverse("shopping_list"))
        self.assertContains(response, 'item-name">Salt')
        self.assertNotContains(response, "Assumed you have")

    def test_unmatched_staple_is_not_disclosed(self):
        self.plan_recipe_with(("Butter", 200, "g"))
        Staple.objects.create(name="saffron")
        response = self.client.get(reverse("shopping_list"))
        self.assertNotContains(response, "Assumed you have")

    def test_staple_does_not_hide_a_matching_extra(self):
        Staple.objects.create(name="Olive oil")
        Extra.objects.create(name="Olive oil")
        response = self.client.get(reverse("shopping_list"))
        self.assertContains(response, 'item-name">Olive oil')

    def test_clear_plan_keeps_staples(self):
        self.plan_recipe_with(("Salt", 1, "pinch"))
        Staple.objects.create(name="Salt")
        self.client.post(reverse("clear_plan"))
        self.assertEqual(Staple.objects.count(), 1)


class ThemeSettingsTests(TestCase):
    """The Settings page and the per-user theme choice (ticket 01)."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")

    def test_settings_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="theme"')
        for value in ("system", "light", "dark"):
            self.assertContains(response, f'value="{value}"')

    def test_post_saves_each_valid_theme_and_html_reflects_it(self):
        self.client.force_login(self.user)
        for value in ("light", "dark", "system"):
            with self.subTest(theme=value):
                response = self.client.post(reverse("settings"), {"theme": value})
                self.assertRedirects(response, reverse("settings"))
                self.assertEqual(
                    UserSetting.objects.get(user=self.user).theme, value
                )
                # A subsequent page load renders the chosen theme server-side.
                response = self.client.get(reverse("recipe_list"))
                self.assertContains(response, f'data-theme="{value}"')

    def test_post_shows_success_toast_on_settings_page(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("settings"), {"theme": "dark"}, follow=True
        )
        self.assertContains(response, "Settings saved.")

    def test_invalid_theme_value_does_not_save(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("settings"), {"theme": "neon"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            UserSetting.objects.filter(user=self.user)
            .exclude(theme="system")
            .exists()
        )

    def test_login_page_for_anonymous_carries_system_theme(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, 'data-theme="system"')

    def test_pages_default_to_system_theme_without_a_setting(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(response, 'data-theme="system"')

    def test_settings_link_in_nav_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(response, f'href="{reverse("settings")}"')

    def test_forced_theme_uses_single_theme_color_meta(self):
        self.client.force_login(self.user)
        UserSetting.objects.create(user=self.user, theme="dark")
        response = self.client.get(reverse("recipe_list"))
        self.assertNotContains(
            response, '<meta name="theme-color" media=', html=False
        )
        self.assertContains(response, '<meta name="theme-color" content="#1c1917">')


class RecipeSortOrderTests(TestCase):
    """Recipe.sort_order and the drag-to-reorder feature (ticket 01)."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)

    def test_recipes_ordered_by_sort_order_then_name(self):
        Recipe.objects.create(name="Apple pie", sort_order=30)
        Recipe.objects.create(name="Zebra cake", sort_order=10)
        # Equal sort_order falls back to the name.
        Recipe.objects.create(name="Bread", sort_order=20)
        Recipe.objects.create(name="Aioli", sort_order=20)
        self.assertEqual(
            [r.name for r in Recipe.objects.all()],
            ["Zebra cake", "Aioli", "Bread", "Apple pie"],
        )

    def test_data_migration_assigns_10_20_30_by_name(self):
        """The data migration gives existing recipes 10, 20, 30... by name."""
        Recipe.objects.create(name="Carbonara")
        Recipe.objects.create(name="Apple pie")
        Recipe.objects.create(name="Bread")
        migration = import_module("meals.migrations.0006_recipe_sort_order_data")
        migration.assign_sort_order(django_apps, None)
        self.assertEqual(
            list(Recipe.objects.values_list("name", "sort_order")),
            [("Apple pie", 10), ("Bread", 20), ("Carbonara", 30)],
        )

    def new_recipe_payload(self, name):
        return {
            "name": name,
            "servings": "",
            "instructions": "",
            "ing_name": ["Water"],
            "ing_qty": ["1"],
            "ing_unit": ["l"],
        }

    def test_new_recipe_appended_at_end(self):
        Recipe.objects.create(name="Zebra cake", sort_order=40)
        self.client.post(reverse("recipe_new"), self.new_recipe_payload("Apple pie"))
        self.assertEqual(Recipe.objects.get(name="Apple pie").sort_order, 50)
        # Alphabetically first, but rendered last.
        self.assertEqual(
            [r.name for r in Recipe.objects.all()], ["Zebra cake", "Apple pie"]
        )

    def test_first_recipe_gets_sort_order_10(self):
        self.client.post(reverse("recipe_new"), self.new_recipe_payload("Soup"))
        self.assertEqual(Recipe.objects.get(name="Soup").sort_order, 10)

    def test_editing_a_recipe_keeps_its_sort_order(self):
        recipe = Recipe.objects.create(name="Soup", sort_order=30)
        self.client.post(
            reverse("recipe_edit", args=[recipe.pk]),
            self.new_recipe_payload("Better Soup"),
        )
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Better Soup")
        self.assertEqual(recipe.sort_order, 30)

    def test_planning_page_renders_recipes_by_sort_order_with_handles(self):
        Recipe.objects.create(name="Apple pie", sort_order=20)
        Recipe.objects.create(name="Zebra cake", sort_order=10)
        response = self.client.get(reverse("recipe_list"))
        content = response.content.decode()
        self.assertLess(content.index("Zebra cake"), content.index("Apple pie"))
        self.assertEqual(content.count('class="drag-handle"'), 2)
        for recipe in Recipe.objects.all():
            self.assertContains(response, f'data-id="{recipe.id}"')


class ReorderRecipesTests(TestCase):
    """The reorder_recipes endpoint saving the shared drag-and-drop order."""

    def setUp(self):
        self.user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(self.user)
        self.apple = Recipe.objects.create(name="Apple pie", sort_order=10)
        self.bread = Recipe.objects.create(name="Bread", sort_order=20)
        self.soup = Recipe.objects.create(name="Soup", sort_order=30)

    def post_order(self, ids):
        return self.client.post(
            reverse("reorder_recipes"), {"order": ",".join(str(i) for i in ids)}
        )

    def current_order(self):
        return list(Recipe.objects.values_list("name", "sort_order"))

    def test_form_encoded_order_saves_10_20_30(self):
        response = self.post_order([self.soup.id, self.apple.id, self.bread.id])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertEqual(
            self.current_order(),
            [("Soup", 10), ("Apple pie", 20), ("Bread", 30)],
        )

    def assert_nothing_saved(self):
        self.assertEqual(
            self.current_order(),
            [("Apple pie", 10), ("Bread", 20), ("Soup", 30)],
        )

    def test_unknown_id_rejected_and_nothing_saved(self):
        response = self.post_order(
            [self.soup.id, self.apple.id, self.bread.id, 9999]
        )
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_missing_id_rejected_and_nothing_saved(self):
        response = self.post_order([self.soup.id, self.apple.id])
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_duplicate_id_rejected_and_nothing_saved(self):
        response = self.post_order(
            [self.soup.id, self.apple.id, self.bread.id, self.soup.id]
        )
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_non_integer_ids_rejected(self):
        response = self.client.post(reverse("reorder_recipes"), {"order": "a,b,c"})
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_empty_order_rejected_when_recipes_exist(self):
        response = self.client.post(reverse("reorder_recipes"), {"order": ""})
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_invalid_json_body_rejected(self):
        response = self.client.post(
            reverse("reorder_recipes"), "not json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_json_order_must_be_a_list(self):
        response = self.client.post(
            reverse("reorder_recipes"),
            json.dumps({"order": "1,2,3"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assert_nothing_saved()

    def test_get_not_allowed(self):
        response = self.client.get(reverse("reorder_recipes"))
        self.assertEqual(response.status_code, 405)


class PwaTests(TestCase):
    """The web app manifest and icons that make Cookbook installable."""

    def load_manifest(self):
        """Read the manifest through the staticfiles finders."""
        path = finders.find("meals/manifest.webmanifest")
        self.assertIsNotNone(path, "manifest.webmanifest not found by finders")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_manifest_declares_installable_app(self):
        manifest = self.load_manifest()
        self.assertEqual(manifest["name"], "Cookbook")
        self.assertEqual(manifest["short_name"], "Cookbook")
        self.assertEqual(manifest["start_url"], "/")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["background_color"], "#faf8f5")
        self.assertEqual(manifest["theme_color"], "#f97316")

    def test_manifest_icons_point_at_existing_static_files(self):
        icons = self.load_manifest()["icons"]
        self.assertEqual(
            sorted(icon["sizes"] for icon in icons), ["192x192", "512x512"]
        )
        for icon in icons:
            with self.subTest(src=icon["src"]):
                self.assertTrue(icon["src"].startswith(settings.STATIC_URL))
                relative = icon["src"][len(settings.STATIC_URL):]
                self.assertIsNotNone(
                    finders.find(relative), f"{icon['src']} does not resolve"
                )

    def test_manifest_url_serves_valid_json(self):
        """The manifest URL itself serves JSON, without requiring login.

        WhiteNoise serves from the staticfiles finders here (no
        collectstatic output exists during tests).
        """
        with self.settings(WHITENOISE_USE_FINDERS=True, WHITENOISE_AUTOREFRESH=True):
            response = self.client.get(
                settings.STATIC_URL + "meals/manifest.webmanifest"
            )
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content if response.streaming else [response.content])
        manifest = json.loads(body)
        self.assertEqual(manifest["name"], "Cookbook")

    def test_base_template_links_manifest_and_apple_touch_icon(self):
        user = User.objects.create_user("partner", password="test-pass-123")
        self.client.force_login(user)
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(response, 'rel="manifest"')
        self.assertContains(response, 'rel="apple-touch-icon"')
