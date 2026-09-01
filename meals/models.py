from django.db import models


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

    class Meta:
        ordering = ["name"]

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


class PlanEntry(models.Model):
    """A recipe currently selected in the shared meal plan."""

    recipe = models.OneToOneField(
        Recipe, on_delete=models.CASCADE, related_name="plan_entry"
    )

    class Meta:
        verbose_name_plural = "plan entries"

    def __str__(self):
        return f"Planned: {self.recipe.name}"
