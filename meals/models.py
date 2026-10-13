from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class Unit(models.TextChoices):
    GRAM = "g", "g"
    KILOGRAM = "kg", "kg"
    MILLILITER = "ml", "ml"
    LITER = "l", "l"
    PIECE = "pcs", "pcs"
    TABLESPOON = "tbsp", "tbsp"
    TEASPOON = "tsp", "tsp"
    CUP = "cup", "cup"
    PINCH = "pinch", "pinch"


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Shared manual position on the planning page; spaced in steps of 10
    # (10, 20, 30...) so the reorder endpoint can rewrite it cheaply.
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    name = models.CharField(max_length=200)
    quantity = models.FloatField()
    unit = models.CharField(max_length=10, choices=Unit.choices)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class CookingDay(models.Model):
    """A day in the Rolling Week the couple marked as a day they cook.

    Shared by both users; not linked to specific Recipes.
    """

    date = models.DateField(unique=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Cooking day: {self.date.isoformat()}"


class Extra(models.Model):
    """An off-plan shared shopping line added directly on the Shopping List.

    Free text only, not part of any Recipe. Shared by both users; wiped
    together with the Meal Plan by Clear plan.
    """

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name


class Staple(models.Model):
    """An ingredient name the household always has at home (see GLOSSARY.md).

    Shared by both users and managed on the Settings page. The Shopping
    List skips recipe-derived lines matching a Staple case-insensitively
    and discloses them as assumed-at-home. Staples never hide Extras.
    """

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [Lower("name")]
        constraints = [
            models.UniqueConstraint(
                Lower("name"), name="staple_name_case_insensitive_unique"
            )
        ]

    def __str__(self):
        return self.name


class Theme(models.TextChoices):
    SYSTEM = "system", "System"
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"


class UserSetting(models.Model):
    """Per-user preferences. One row per user, created on first save."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="setting"
    )
    theme = models.CharField(
        max_length=10, choices=Theme.choices, default=Theme.SYSTEM
    )

    def __str__(self):
        return f"Settings for {self.user.username} (theme: {self.theme})"


class PlanEntry(models.Model):
    """A recipe currently selected in the shared meal plan."""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE, related_name="plan_entry"
    )

    class Meta:
        verbose_name_plural = "plan entries"

    def __str__(self):
        return f"Planned: {self.recipe.name}"
