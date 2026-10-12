# 01: Drag-and-drop recipe ordering

**What to build:** On the planning page, either partner can drag recipe
cards into a custom order using a drag handle. The order is saved to the
database, shared by both partners, and replaces the current alphabetical
sort. It must work with touch on phones, not only with a mouse.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `Recipe.sort_order` integer field (default 0); `Meta.ordering` becomes `["sort_order", "name"]`; a data migration assigns existing recipes 10, 20, 30... in current alphabetical order
- [x] Creating a recipe appends it at the end (sort_order = current max + 10)
- [x] Each recipe card gets a visible drag handle (a grip icon area, comfortable touch target, cursor: grab); dragging anywhere else on the card keeps today's select/expand behavior
- [x] Drag and drop implemented with vanilla JS **pointer events** (pointerdown on the handle + setPointerCapture, so one code path serves mouse and touch; `touch-action: none` on the handle); while dragging, the lifted card follows the pointer as a ghost and the drop position is indicated (e.g. cards shift or a placeholder gap)
- [x] On drop, the new order of ALL recipe ids is POSTed (fetch + CSRF, same pattern as the Cooking Day toggle) to a `reorder_recipes` endpoint that validates the ids and saves sort_order 10, 20, 30...; failure response restores the previous DOM order
- [x] Works in the two-column desktop grid and the single-column phone layout (reordering is by visual position in the grid's DOM order)
- [x] While the search filter is active, drag handles are disabled (reordering a filtered subset is ambiguous)
- [x] Dark and light themes style the handle and the dragging state acceptably
- [x] Tests: data migration ordering, reorder endpoint happy path + validation (unknown id, missing ids -> 400, nothing saved), new recipe appended last, planning page renders recipes by sort_order and contains the handles
- [x] Existing 56 tests stay green
