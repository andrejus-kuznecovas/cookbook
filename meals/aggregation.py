"""Pure shopping-list aggregation logic.

Takes ingredient rows from the planned recipes and stacks quantities of the
same ingredient. Metric units are converted to a base unit (g / ml) before
summing so "1 kg flour" and "300 g flour" combine into one line. The same
ingredient name in incompatible units (e.g. grams vs cups) stays as separate
lines because guessing density-based conversions would produce wrong lists.
"""

from dataclasses import dataclass, field

# unit -> (base unit, multiplier to base)
_TO_BASE = {
    "kg": ("g", 1000.0),
    "l": ("ml", 1000.0),
}

# base unit -> (bigger display unit, threshold)
_DISPLAY_UP = {
    "g": ("kg", 1000.0),
    "ml": ("l", 1000.0),
}


@dataclass
class AggregatedLine:
    name: str  # first-seen original casing
    quantity: float  # in base unit
    unit: str  # base unit
    recipes: list = field(default_factory=list)  # contributing recipe names

    @property
    def display_quantity(self) -> str:
        qty, unit = self.quantity, self.unit
        up = _DISPLAY_UP.get(unit)
        if up and qty >= up[1]:
            qty, unit = qty / up[1], up[0]
        text = f"{qty:.2f}".rstrip("0").rstrip(".")
        return f"{text} {unit}"


def to_base(quantity: float, unit: str) -> tuple[float, str]:
    base_unit, factor = _TO_BASE.get(unit, (unit, 1.0))
    return quantity * factor, base_unit


def aggregate(ingredients) -> list[AggregatedLine]:
    """Aggregate an iterable of (name, quantity, unit, recipe_name) tuples
    or Ingredient-like objects into stacked shopping-list lines,
    sorted alphabetically by ingredient name.
    """
    lines: dict[tuple[str, str], AggregatedLine] = {}
    for item in ingredients:
        if isinstance(item, tuple):
            name, quantity, unit, recipe_name = item
        else:
            name, quantity, unit = item.name, item.quantity, item.unit
            recipe_name = item.recipe.name

        base_qty, base_unit = to_base(quantity, unit)
        key = (name.strip().lower(), base_unit)

        line = lines.get(key)
        if line is None:
            line = AggregatedLine(name=name.strip(), quantity=0.0, unit=base_unit)
            lines[key] = line
        line.quantity += base_qty
        if recipe_name not in line.recipes:
            line.recipes.append(recipe_name)

    return sorted(lines.values(), key=lambda l: (l.name.lower(), l.unit))
