# Cookbook

A Django meal planner for two people (the owner and his girlfriend): store
recipes with ingredients, pick meals for the coming days, and get one
aggregated shopping list where shared ingredients stack (200 g + 300 g butter
= 500 g butter). See `README.md` for user-facing docs and local setup.

**Live app:** https://ankuzcookbook.pythonanywhere.com (PythonAnywhere free
tier, account `ankuzcookbook`). Both partners use it from their phones via
the browser; every page requires login, there is no self-signup.

## Stack and key decisions

- Python 3.13, Django 6.1, SQLite, WhiteNoise for static files.
- Server-rendered templates with vanilla JavaScript. No SPA, no frontend
  framework, no build step ([ADR-0001](docs/adr/0001-server-rendered-django.md)).
- SQLite is the production database, living on PythonAnywhere's persistent
  disk; backup = download `db.sqlite3` ([ADR-0002](docs/adr/0002-sqlite-in-production.md)).
- All state is shared between the two users (Meal Plan, Cooking Days,
  Extras) except the per-user theme (`UserSetting`) and shopping-list
  tick-offs (browser `localStorage` on purpose, so two people can split a shop).

## Layout

```
config/            settings (env-driven for prod), urls, wsgi, custom test runner
meals/
  models.py        Unit, Recipe (sort_order), Ingredient, PlanEntry,
                   CookingDay, Extra, UserSetting
  aggregation.py   pure shopping-list stacking logic (unit tested)
  views.py         all views; every view is @login_required
  context_processors.py  injects the user's theme into templates
  templates/meals/ base, recipe_list, recipe_form, shopping_list, settings
  tests.py         the full test suite (70+ tests)
seed.py            optional example data (`manage.py shell -c "import seed"`)
docs/adr/          architecture decision records
.github/           CI workflow + PythonAnywhere deploy script
.scratch/          local markdown issue tracker (see below)
.agents/skills/    installed agent skills (this repo doubles as the owner's
                   skill collection; don't edit skills while doing app work)
```

## Commands (Windows PowerShell; venv at `.venv`)

```powershell
.\.venv\Scripts\python manage.py runserver        # dev server, localhost:8000
.\.venv\Scripts\python manage.py test             # run tests (always before pushing)
.\.venv\Scripts\python manage.py makemigrations   # CI fails on missing migrations
```

Dev database login: `admin` / `cookbook`.

## Conventions

- **Vocabulary:** use the terms in `GLOSSARY.md` (Recipe, Ingredient, Meal
  Plan, Cooking Day, Shopping List, Extra, Stacking, Pick-up Tick, Rolling
  Week) in code, tests, and tickets. Don't drift to the synonyms it lists
  as avoided. If a needed term is missing, that's a gap for `/domain-modeling`.
- **Frontend:** JavaScript lives inline in the template that uses it. Theming
  uses CSS custom properties keyed off `html[data-theme]`, which is rendered
  server-side (context processor) to avoid flicker. Keep the UI compact and
  mobile-first; it is used mostly on phones.
- **Drag and drop** (recipe reordering on the home page) uses pointer events
  bound to `window` on `pointerdown` — NOT `setPointerCapture`, which breaks
  when `insertBefore` moves the dragged card in the DOM. Keep it that way.
- **Views:** keep `@login_required` on every view. Mutations are POST with
  CSRF; JSON endpoints return `JsonResponse` with proper status codes.
- **ADRs:** if a change contradicts an ADR, surface it explicitly instead of
  silently overriding (see `docs/agents/domain.md`).

## Deployment (automatic)

Push to `main` → GitHub Actions (`.github/workflows/ci.yml`) runs tests,
system checks, migration dry-run, and `collectstatic`; if green, the `deploy`
job calls `.github/scripts/deploy_pythonanywhere.py`, which runs
`git pull` / `pip install` / `migrate` / `collectstatic` in a PythonAnywhere
console and reloads the web app. Needs the `PA_API_TOKEN` repo secret and a
running console (id in the workflow).

Known failure: "the deploy console is not running" after PythonAnywhere
maintenance — open the console URL once in a browser, then re-run the job.
Manual fallback and full runbook: `DEPLOYMENT.md`.

Free-tier keep-alive: the web app expires after a month without owner
activity; the owner must click "Run until... (extend)" on the Web tab.

## Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`
(spec in `spec.md`, one ticket per file under `issues/`, `Status:` line for
triage state). See `docs/agents/issue-tracker.md`. Past efforts: `go-live`,
`polish`, `settings-theme`, `recipe-order`.

## Workflow notes

- For multi-ticket features, past sessions ran parallel implementer
  subagents in git worktrees (`../cookbook-worktrees/<branch>`), then merged
  branches sequentially into an integration branch and resolved conflicts
  (usually in `base.html`, `views.py`, `tests.py`).
- Run the full test suite and `manage.py check` before pushing; a push to
  `main` deploys to production.
