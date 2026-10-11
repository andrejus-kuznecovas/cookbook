# Glossary

The canonical vocabulary for the Cookbook project. Use these terms in code,
tickets, tests, and conversation. Avoid the listed synonyms.

## Recipe

A dish the couple can cook: a name, optional instructions and servings, and
its list of Ingredients. Created and edited in the app by the users.

## Ingredient

One line inside a Recipe: a name, a quantity, and a Unit (`g`, `kg`, `ml`,
`l`, `pcs`, `tbsp`, `tsp`, `cup`, `pinch`). Ingredients belong to exactly one
Recipe; the same food in two Recipes is two Ingredient rows.

## Meal Plan

The shared set of Recipes currently selected for the coming days. There is
exactly one Meal Plan, shared by both users; saving a selection replaces it.
Avoid: "selection", "plan entries" (the model name `PlanEntry` implements
one Meal Plan membership).

## Cooking Day

A calendar day the couple has marked as a day they intend to cook, within
the rolling 7-day window shown on the planning page. Shared by both users.
Not linked to specific Recipes. Avoid: "marked day", "day mark".

## Shopping List

The aggregated ingredient lines computed from the Meal Plan's Recipes.
Derived, never stored.

## Stacking

Combining Ingredient quantities of the same normalized name and compatible
unit into one Shopping List line (metric units convert to a base: kg to g,
l to ml). The same name in incompatible units stays as separate lines.

## Pick-up Tick

A personal checkbox on a Shopping List line, used while shopping. Private to
each device (browser localStorage), deliberately not shared: two people can
split a shop. Avoid: "check-off".

## Rolling Week

The 7-day window starting today, shown on the planning page. Never shows
past days; Cooking Days outside the window are pruned.
