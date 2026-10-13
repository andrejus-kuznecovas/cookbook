# Spec: Pantry Staples

**Status:** done

## Problem Statement

The Shopping List tells the couple to buy salt, olive oil, and pepper every
week, even though those are always in the pantry. Lines for things they
never need to buy add noise to every shop and bury the items that actually
matter. There is no way to tell the app "we always have this at home".

## Solution

A shared Staples list: ingredient names the household always has. Staples
are managed on the Settings page (add via text input, remove per item) and
are shared between both users, like Extras and the Meal Plan. The Shopping
List skips recipe-derived lines whose ingredient name matches a staple
case-insensitively, and discloses what it skipped in a collapsed
"Assumed you have: …" details section below the list, so nothing is
silently dropped. Extras are never filtered: an Extra is an explicit user
request, even if it matches a staple name.

## User Stories

1. As a partner, I want to mark salt and olive oil as staples, so the
   shopping list stops telling me to buy them every week
2. As a partner, I want to see which ingredients the list assumed we have,
   so I can double-check the pantry before shopping
3. As a partner, I want staples my partner added to apply to my shopping
   list too, so we maintain one list together
4. As a partner, I want to remove a staple when we run out of it for good,
   so it shows up on the list again
5. As a partner, I want an Extra I typed in to always stay on the list,
   even if it matches a staple, because I asked for it explicitly

## Implementation Decisions

- New model `Staple`: a single `name` field, shared household-wide (no
  user FK). Case-insensitive uniqueness is enforced both in the add view
  (`iexact` check, silently a no-op on duplicates) and at the database
  level with a functional unique constraint on `Lower("name")`.
- Aggregation stays pure (`meals/aggregation.py`). `aggregate()` is
  unchanged; a new pure function `split_staples(lines, staple_names)`
  partitions aggregated lines into (lines to buy, assumed staple names).
  The view passes staple names in; aggregation never touches the ORM.
- The disclosure section renders only when at least one line was skipped.
  With no staples defined (or none matching), the Shopping List is
  byte-for-byte what it was before this feature.
- Views `add_staple` / `remove_staple` follow `add_extra` / `remove_extra`:
  `@login_required`, `@require_POST`, CSRF, redirect back to Settings.
  Whitespace-only names are rejected silently.
- Settings page gains a "Staples" card: current staples each with a
  remove button (reusing the Extras remove-button pattern, 2.25rem
  targets) and an add form (text input + Add button).
- Styling uses only existing CSS custom properties so light and dark
  themes both work; text on accent fills uses `--accent-fill` /
  `--accent-fill-strong`, never `--accent`.
- `Clear plan` does not touch Staples: they are standing household
  configuration, not part of any one plan.

## Testing Decisions

- Seams (same as the rest of the suite): the pure functions in
  `meals/aggregation.py` tested directly with tuples, and the views
  tested through Django's test client. No new seams.
- Aggregation: staples skipped case-insensitively; a staple name in mixed
  units removes every line of that name; empty staple list returns input
  unchanged; assumed names come back for the disclosure.
- Views: add/remove staple; duplicate (case-insensitive) add is a silent
  no-op; whitespace-only rejected; both new URLs redirect anonymous users
  to login; Settings page lists staples.
- Shopping List page: staple lines excluded; disclosure section present
  with the staple names; disclosure absent with no staples; an Extra
  matching a staple still renders.

## Out of Scope

- Per-user staples (shared by design, like Extras)
- Quantity-aware staples ("we have 500 g of flour")
- Suggesting staples from shopping history
- Filtering Extras against staples (explicitly excluded: an Extra is an
  explicit request)
