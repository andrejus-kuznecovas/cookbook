# 03: Shopping list Extras

**What to build:** While looking at the Shopping List, either partner can
add free-form items that aren't part of any Recipe ("dish soap", "coffee
beans"). Extras are shared (database-backed), appear in their own section
under the aggregated lines, can be removed individually, and are wiped
together with Clear plan.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `Extra` model: a `name` CharField and `created_at` (no quantity/unit - free text name is enough); migration included
- [ ] Add-extra form on the shopping list page (one text input + add button, normal POST, redirect back); empty/whitespace names rejected silently
- [ ] Extras render in an "Extras" section under the aggregated Shopping List with the same check-off ring styling; their Pick-up Ticks join the existing localStorage mechanism (key per extra)
- [ ] Each extra has a small remove control (POST)
- [ ] Clear plan also deletes all Extras
- [ ] Extras appear even when no meals are selected (the shopping page shows the extras section + add form instead of only the empty state)
- [ ] GLOSSARY.md gains an "Extra" entry (off-plan shared shopping line)
- [ ] Tests: add, reject-empty, remove, clear-plan wipes extras, extras visible to another authenticated user; existing tests stay green
