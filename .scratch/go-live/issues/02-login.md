# 02: Login required everywhere

**What to build:** An anonymous visitor to any app page is redirected to a
login page styled like the rest of the app; after logging in they land
where they were heading. A logged-in partner sees a logout control in the
header. No app page or endpoint is reachable without authentication.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] All meals views require login (anonymous GET/POST to every URL in `meals/urls.py` redirects to the login page with `next` preserved)
- [x] Login page at `/accounts/login/` uses Django auth views with a template matching the app's look (orange theme, card layout, mobile-friendly)
- [x] Logout is a POST control in the header, visible only when authenticated, redirecting back to login
- [x] `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` configured
- [x] README gains a short "accounts" note: create users via `createsuperuser` or the admin
- [x] Tests: anonymous redirect for every URL, authenticated 200 on the planning page, logout flow
- [x] Existing 14 tests still pass (update them to authenticate where needed)
