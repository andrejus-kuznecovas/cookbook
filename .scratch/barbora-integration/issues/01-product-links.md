# Barbora product links on the Shopping List

Status: done

## What

Every line on the Shopping List (recipe-derived lines AND Extras) can carry a
link to the exact barbora.lt product the household buys for it. Mapped lines
show a "Barbora" link that opens the product page in a new tab, where
Barbora's own add-to-cart is one tap. Unmapped lines offer a small inline
"link a product" affordance to teach the mapping once.

## Model

`BarboraLink`
- `name` — CharField(200). Matches shopping lines by name, case-insensitive.
  Database-level case-insensitive unique constraint (`Lower("name")`), same
  pattern as `Staple`.
- `url` — URLField. Must start with `https://barbora.lt/` or
  `https://www.barbora.lt/`; reject anything else at the view level.
- Shared household-wide, like Extras and Staples. Migration required.

Add "Barbora Link" to GLOSSARY.md (a shopping line's remembered barbora.lt
product URL; avoid synonyms "mapping", "product link" in code).

## Views (all @login_required, POST + CSRF, redirect back to shopping list
or settings as appropriate — mirror add_extra/remove_extra style)

- `add_barbora_link` — POST name + url. UPSERT: if a link with that name
  exists (any casing), replace its url. Whitespace-only name or invalid url
  → redirect back without creating (no crash); invalid url shows a Django
  message (the base template already renders messages as toasts).
- `remove_barbora_link` — POST by pk, from the Settings page.

## UI

Shopping List (`shopping_list.html`):
- IMPORTANT structural note: recipe-derived lines are currently a `<label
  class="shop-item">` wrapping the whole row. A link inside a label toggles
  the checkbox. Restructure recipe lines to the Extras pattern: outer
  `div.shop-item` containing an inner `label.extra-label`-style wrapper for
  checkbox+ring+text, with the Barbora link/affordance OUTSIDE the label as
  a sibling (like `.extra-remove`). Keep the tick-off behavior and
  localStorage keys exactly as they are.
- Mapped line: icon link (shopping-bag or external-link SVG, consistent
  with existing inline SVG style) with `aria-label="Open <name> on Barbora"`,
  `target="_blank" rel="noopener"`, tap target ≥ 2.25rem. Also on Extras
  rows (placed before the remove button).
- Unmapped line: a muted "+" style affordance with
  `aria-label="Link <name> to a Barbora product"` that reveals an inline
  form (a `<details>` per line, or one shared form at the card bottom that
  JS prefills with the tapped name — implementer's choice, keep JS inline
  and small) with a URL field (`placeholder="Paste barbora.lt product
  link"`, `inputmode="url"`) and a save button posting to
  `add_barbora_link` with the line's name.
- The "Assumed you have" staples disclosure gets no links.

Settings (`settings.html`):
- New "Barbora links" card listing all `BarboraLink` rows (name + shortened
  url text, link opens product) with a per-row remove button — mirror the
  Staples management UI added in commit 3dcc5e9.

## Seeding

Management command `load_barbora_links <path.json>`: JSON object of
`{"ingredient name": "https://barbora.lt/..."}`, idempotent upsert, prints
a summary (created/updated/skipped-invalid). Unit tested. No JSON file is
committed in this ticket; the owner runs it with his own file (or pastes
links in the UI).

## Accessibility (do not regress the HIG pass)

- Use CSS custom properties only; never white text on `var(--accent)` —
  use `var(--accent-fill)`. Both light and dark themes; the two dark-mode
  blocks in base.html must stay identical if touched.
- Tap targets ≥ 2.25rem for the new icon link/affordance; text ≥ 0.75rem.
- Keyboard focus stays visible (global :focus-visible rule exists).

## Tests (TDD — red first)

- Model: case-insensitive unique constraint.
- add view: creates; upserts on same name different casing; rejects non-
  barbora URLs and blank names without creating; login required.
- remove view: removes; login required.
- Shopping list: mapped recipe line shows the product URL; match is
  case-insensitive ("Butter" line matches "butter" link); extras get links
  too; unmapped lines show the teach affordance, not a product link;
  staple-filtered lines show no links.
- Settings: lists links, remove works.
- Management command: creates, updates, skips invalid, idempotent.

## Out of scope

- Package-size math, quantity suggestions.
- Any server-side calls to barbora.lt (hosting cannot reach it; see spec).
- Auto-translation of names to Lithuanian.
- Cart push (phase 3).
