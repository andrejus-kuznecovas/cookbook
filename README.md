# Cookbook — Weekly Meal Planner

A small Django app for two people to store recipes, pick meals for the next
few days, and get one combined shopping list where shared ingredients stack
(200 g + 300 g butter = 500 g butter, 1 kg + 300 g flour = 1.3 kg flour).

## How it works

- **Add / edit recipes** in the app itself (`/recipes/new/`, or "Edit recipe"
  inside a recipe card) — a mobile-friendly form with dynamic ingredient rows.
  The Django admin (`/admin`) also works as a power-user fallback.
- **Pick meals** on the home page (`/`) — tap the recipes you plan to cook
  and save. The selection is stored in the database, so it is shared.
- **Shopping list** (`/shopping-list/`) shows the aggregated ingredients for
  the selected recipes, with tick-off checkboxes (remembered in the browser)
  for use in the store.

Units: `g`, `kg`, `ml`, `l`, `pcs`, `tbsp`, `tsp`, `cup`, `pinch`.
Metric units stack across recipes (kg with g, l with ml). The same ingredient
in incompatible units (e.g. grams vs cups) is shown as separate lines.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser   # login for /admin
.\.venv\Scripts\python manage.py shell -c "import seed"   # optional example recipes
.\.venv\Scripts\python manage.py runserver
```

Open http://localhost:8000 — recipes at `/admin` (the dev database already has
user `admin` / password `cookbook`; change it or create your own).

On macOS/Linux replace `.\.venv\Scripts\` with `.venv/bin/`.

## Tests

```powershell
.\.venv\Scripts\python manage.py test
```

Covers the shopping-list aggregation logic (stacking, kg/g and l/ml
conversion, incompatible units, name normalization, display formatting).

## Project layout

```
config/            Django project settings and root urls
meals/
  models.py        Recipe, Ingredient, PlanEntry
  admin.py         Recipe admin with inline ingredient editing
  aggregation.py   pure shopping-list stacking logic (unit tested)
  views.py         recipe list + shopping list + clear plan
  templates/meals/ base, recipe list, shopping list
seed.py            optional example data
```

## Deploying later (one shared URL for both phones)

Not set up yet, but the app is ready for it:

1. Host on a free tier that keeps a persistent disk for `db.sqlite3` —
   **PythonAnywhere** (built for Django, no card required) or **Render**.
2. Before going public, set in `config/settings.py`: `DEBUG = False`,
   a secret `SECRET_KEY` from an env var, and your domain in `ALLOWED_HOSTS`;
   protect the pages with Django's built-in login (`login_required` on the
   views) and create one account per person.
3. On both phones, open the URL in the browser and use "Add to Home Screen"
   for an app-like icon. An Android APK is possible later by wrapping the
   deployed URL in a Trusted Web Activity, but is not required.
