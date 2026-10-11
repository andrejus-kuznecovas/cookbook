# Spec: Go Live

**Status:** done

## Problem Statement

The Cookbook app works on localhost only. The couple cannot use it from
their phones in daily life: there is no shared URL, no protection against
strangers once public, Cooking Days are trapped per-device in localStorage
instead of shared, and the app does not install to a phone home screen.
Production-unsafe settings (hardcoded SECRET_KEY, DEBUG=True, no static
file serving story) block deployment.

## Solution

Deploy the app to PythonAnywhere's free tier under one URL both partners
use. All pages require login with one Django account per partner. Cooking
Days move to the database so both partners see the same marked days. A web
app manifest and icons make the app installable to the home screen on
Android and iOS. A written deployment runbook covers the manual
PythonAnywhere steps the owner must perform.

## User Stories

1. As a partner, I want to open one URL on my phone and see our shared recipes, so that we can plan meals from anywhere
2. As a partner, I want the app to require a login, so that strangers cannot see or edit our recipes
3. As a partner, I want to log in once and stay logged in on my phone, so that daily use is frictionless
4. As a partner, I want to log out, so that I can switch accounts or secure a shared device
5. As a partner, I want my meal selections visible to my partner, so that we plan together (already works; must keep working in production)
6. As a partner, I want the Cooking Days I mark to be visible to my partner, so that we agree on which days we cook
7. As a partner, I want unmarking a Cooking Day to be shared too, so that plans stay in sync
8. As a partner, I want Cooking Days older than today to disappear automatically, so that the calendar stays current
9. As a partner, I want to add the app to my phone's home screen with a proper icon and name, so that it feels like an app
10. As a partner, I want the app to open full-screen from the home screen without browser chrome, so that it feels native
11. As the owner, I want all secrets and host configuration read from the environment, so that the repo stays safe to publish
12. As the owner, I want static files served correctly in production, so that the app looks right when DEBUG is off
13. As the owner, I want a step-by-step deployment runbook, so that I can bring the app live on PythonAnywhere without guesswork
14. As the owner, I want to create our two accounts simply, so that onboarding my partner takes a minute
15. As a partner, I want my private Pick-up Ticks to keep working after login is added, so that shopping flow is unchanged

## Implementation Decisions

- Authentication uses Django's built-in auth: `django.contrib.auth` views
  for login/logout, a login template styled like the app, and
  login-required enforcement across all app views (admin keeps its own).
  Accounts are created with `createsuperuser` / the admin; no self-signup.
- Cooking Day becomes a model with a unique date field. Toggling a day is
  a POST endpoint; the planning page renders marked state server-side for
  the Rolling Week. The localStorage implementation and its pruning logic
  are removed; pruning becomes a server-side delete of past dates done on
  planning-page load.
- The Rolling Week stays 7 days starting today (see glossary).
- Production settings read `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` from
  environment variables with safe development defaults, so `runserver`
  keeps working with zero configuration. WhiteNoise serves static files;
  `STATIC_ROOT` is configured and `collectstatic` must run clean.
- PWA: a web app manifest (name, colors matching the orange theme, icons)
  plus apple-touch-icon; icons are committed PNG files. No service worker
  and no offline support in this phase.
- Deployment target is PythonAnywhere free tier with SQLite on persistent
  disk (ADR-0002). The runbook (`DEPLOYMENT.md`) covers: account creation,
  code upload via git, virtualenv, env vars in the WSGI file, static files
  mapping, and smoke checks. Manual steps belong to the owner; agents
  prepare everything scriptable.
- Server-rendered Django throughout; no frontend framework (ADR-0001).

## Testing Decisions

- Tests assert external behavior through the existing seam: Django's test
  client against the views, as `RecipeFormViewTests` already does. No new
  seams.
- Auth: every app URL redirects anonymous users to the login page; an
  authenticated client gets 200s; logout works.
- Cooking Days: toggling marks/unmarks for all users; past days are pruned
  on planning-page load; the planning page renders marked state.
- Settings: with env vars set, `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` take
  the env values; without them, dev defaults apply.
- PWA: the manifest URL serves valid JSON referencing existing icon files;
  base template links it.
- The aggregation suite (9 tests) and recipe form suite (5 tests) must
  keep passing untouched.

## Out of Scope

- Recipe search, categories/tags, photos, servings scaling
- Linking Recipes to specific Cooking Days
- Shared Pick-up Ticks (stay per-device by design; see glossary)
- Service worker / offline mode
- Custom domain, HTTPS configuration beyond what PythonAnywhere provides
- Self-signup, password reset emails

## Further Notes

The owner performs the actual PythonAnywhere signup and console steps;
ticket 05 delivers the runbook plus every file the runbook references.
