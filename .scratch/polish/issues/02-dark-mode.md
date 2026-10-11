# 02: Dark mode

**What to build:** The app follows the phone's appearance setting: in
dark mode every page renders with a dark palette that keeps the orange
accent and passes readable contrast; in light mode nothing changes.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] A `prefers-color-scheme: dark` media query overrides the CSS custom properties in `meals/templates/meals/base.html` (dark surfaces, light text, adjusted borders/shadows, same orange accent family)
- [x] Hardcoded colors outside the variables (header backdrop, toast, error banner, danger button, check rings, chips, day pills, shop items, empty states, login card) are audited and given dark equivalents
- [x] `color-scheme: light dark` is declared so form controls render natively
- [x] The `theme-color` meta adapts (media attribute variant for dark)
- [x] Every page is checked in dark: planning page (calendar, cards, action bar), shopping list, recipe form, login
- [x] No template structure changes beyond the `<head>`/CSS; existing tests stay green
