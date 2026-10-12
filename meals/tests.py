import json
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .aggregation import aggregate
from .models import CookingDay, Extra, Ingredient, PlanEntry, Recipe, UserSetting


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
            (reverse("shopping_list"), ["get", "post"]),
            (reverse("add_extra"), ["get", "post"]),
            (reverse("remove_extra", args=[1]), ["get", "post"]),
            (reverse("clear_plan"), ["get", "post"]),
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
