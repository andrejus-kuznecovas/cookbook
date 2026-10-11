# 01: Recipe search and Surprise me

**What to build:** With 20+ recipes the planning page needs fast finding:
typing in a search box instantly filters the recipe cards by name, and a
"Surprise me" button randomly picks 3 recipes for the Meal Plan when the
couple can't decide.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A search input above the recipe grid filters cards by recipe name as you type (case-insensitive substring, vanilla JS, no server round-trip); a clear (x) affordance resets it
- [ ] When no card matches, a short "No recipes match" note appears
- [ ] Filtering never unchecks selections; hidden selected cards still submit
- [ ] A "Surprise me" control selects 3 random recipes (replacing the current client-side selection, not yet saved) and updates the selected count; user can adjust before saving
- [ ] With 3 or fewer recipes, Surprise me selects all of them
- [ ] Styling matches the design system (pill buttons, cards, orange accent)
- [ ] Tests: planning page contains the search input and surprise control (server-rendered markup); existing tests stay green
