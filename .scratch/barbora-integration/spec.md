# Barbora integration — push the Shopping List toward the barbora.lt cart

Status: idea / spec only, no tickets yet

## Goal

The owner orders groceries on barbora.lt. After building a Shopping List in
the app, he wants the items in the real Barbora cart with as little retyping
as possible.

## Constraints (verified 2026-10-13)

1. **No official Barbora API.** Community tools use the reverse-engineered
   web API (delivery-slot scrapers on GitHub; a Jan 2026 Chrome extension
   "Barbora Agent" adds to cart via the internal API using the user's own
   browser session cookies). In-browser cart calls are proven feasible;
   server-side calls are unsanctioned and fragile.
2. **PythonAnywhere free tier cannot reach barbora.lt.** Outbound HTTPS is
   restricted to an allowlist of official documented APIs. Server-side
   integration is impossible on current hosting and undesirable anyway
   (credential storage, bot protection, ToS).
3. **Language + SKU gap.** Ingredients are English ("Butter"); Barbora sells
   Lithuanian SKUs ("Sviestas ROKIŠKIO 82% 200 g"). A learned mapping
   ingredient-name → chosen product is the core of the feature.
4. **Package math.** The list says "500 g butter"; Barbora sells packages.
   v1: show the needed amount, let the human pick counts. Later:
   ceil(needed / package size) once package size is stored.

## Architecture

The Django app is the brain (list + learned mappings, all server-rendered).
The user's browser is the hands (it is already logged into Barbora).
The server never contacts barbora.lt.

## Phase 1 — Barbora-ready list (small, zero risk)

- "Order on Barbora" section or toggle on the Shopping List: each unticked
  line becomes a link to `https://barbora.lt/paieska?q=<term>`
  (URL pattern verified). Opens in a new tab; on the phone it opens the
  Barbora app/site search.
- New model `BarboraTerm(name_key unique ci, search_term)`: optional
  Lithuanian search term per ingredient name ("butter" → "sviestas").
  Editable inline; lines without a term fall back to the raw name.
- "Copy list" button (plain text) as the lowest-tech export.

## Phase 2 — product memory (small-medium, zero risk, the sweet spot)

- Extend the mapping to a specific product: `product_url` (+ optional
  `package_note`). Teach it by pasting the Barbora product URL once
  (bonus: parse size from the URL/slug when possible).
- Mapped lines link straight to the product page — one tap on Barbora's
  own "add to cart" per item. Unmapped lines keep the search link with a
  "remember this product" affordance (paste URL field).
- No ToS exposure at all; works on phones.

## Phase 3 — true cart push (the real project, desktop, optional)

- **Spike first:** with DevTools on barbora.lt, capture the internal
  endpoints for search and add-to-cart; note auth headers/cookies, CSRF,
  Cloudflare behavior. Decide bookmarklet vs browser extension.
- Cookbook side: token-authenticated read-only JSON endpoint exporting the
  current unticked list + mappings (token because the session cookie is
  SameSite and won't ride cross-site fetches). Plus a POST endpoint so the
  extension can teach new mappings back ("I chose this product for
  'butter'").
- Extension/bookmarklet side: on barbora.lt, fetch the list, add mapped
  items via the internal cart API in-session, surface unmapped items as
  search shortcuts. One click ≈ whole cart.
- Risks: internal API changes silently (keep this layer thin and
  replaceable); technically against the spirit of ToS (personal use, own
  session, low volume — low practical risk); mobile not covered
  (bookmarklets are desktop-bound; extension is Chrome desktop).

## Out of scope

- Server-side login to Barbora, headless browsers on the server, storing
  Barbora credentials anywhere.
- Automatic checkout/delivery-slot booking.

## Glossary candidates

"Barbora term", "Product mapping" — add to GLOSSARY.md if/when implemented
(see /domain-modeling).
