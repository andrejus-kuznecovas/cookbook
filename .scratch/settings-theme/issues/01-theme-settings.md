# 01: Settings page with a theme toggle

**What to build:** A Settings tab where each partner picks the app theme:
System (follow the device, current behavior, default), Light, or Dark.
The choice is stored per user account, applies on every page immediately
after saving, follows the user across devices, and never flashes the
wrong theme (the server renders the chosen theme).

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `UserSetting` model: `user` OneToOneField, `theme` CharField with choices `system` (default) / `light` / `dark`; migration included
- [x] `/settings/` page (login required): a styled segmented control or radio group for the three themes, POST saves and redirects back to Settings with a success toast; invalid values are rejected (400 or form error)
- [x] "Settings" link in the header nav (authenticated users only), active-state styled like the other nav links
- [x] The `<html>` element carries `data-theme="system|light|dark"` server-side for every page, including the login page (anonymous users get `system`) - use a context processor so no view forgets it
- [x] CSS in `base.html` refactored so: `data-theme="dark"` forces the dark palette, `data-theme="light"` forces light, `data-theme="system"` keeps today's `prefers-color-scheme` behavior - visual appearance in both forced modes matches the existing media-query dark/light exactly
- [x] Both `theme-color` metas behave sensibly for forced themes (forced theme may use a single non-media meta)
- [x] Tests: settings page renders for authenticated user, anonymous redirected; POST saves each valid theme and the html tag reflects it on a subsequent page load; invalid theme value does not save; login page for anonymous carries `data-theme="system"`
- [x] Existing 48 tests stay green
