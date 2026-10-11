# 03: Shared Cooking Days

**What to build:** When either partner marks a day in the Rolling Week
calendar, the other partner sees the same mark. Marks live in the database,
not localStorage. Past days disappear automatically.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `CookingDay` model: a unique `date` field (migration included)
- [x] POST endpoint toggles a Cooking Day on/off; the calendar day pills submit to it (progressive enhancement: fetch() with CSRF token, falling back is not required)
- [x] Planning page renders marked state server-side for the Rolling Week; the localStorage `cookbook-days` logic and pruning JS are removed
- [x] Past Cooking Days are deleted server-side when the planning page loads
- [x] Pick-up Ticks (`cookbook-checked` localStorage) are untouched
- [x] Tests: toggle on, toggle off, prune of past days, calendar renders marked state
- [x] Existing 14 tests still pass
