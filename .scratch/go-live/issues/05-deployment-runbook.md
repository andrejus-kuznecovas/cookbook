# 05: PythonAnywhere deployment runbook

**What to build:** The owner can take the repo from GitHub to a live,
login-protected app at a pythonanywhere.com URL by following one document,
with no guesswork.

**Blocked by:** 01, 02 (settings and auth must be final so the runbook
documents reality).

**Status:** done

- [x] `DEPLOYMENT.md` at the repo root: numbered steps covering PythonAnywhere account creation, cloning the repo, virtualenv + `pip install -r requirements.txt`, migrate, createsuperuser for both partners, setting `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` env vars in the WSGI file, static files mapping to `STATIC_ROOT`, reload, and smoke checks (login, add recipe, shopping list from both accounts)
- [x] The WSGI configuration snippet in the runbook matches this repo's actual module paths and settings names
- [x] A "updating the app later" section: git pull, migrate, collectstatic, reload
- [x] A "backups" section: how to download `db.sqlite3` (per ADR-0002)
- [x] README links to `DEPLOYMENT.md`
- [x] No code changes expected; if a gap is found (something undeployable), fix it minimally and note it in the runbook — one gap found: with `DEBUG=False`, `manage.py check --deploy` failed with `mail.E001` (console mail backend is development-only in Django 6). Fixed by enabling the console `MAILERS` override only when `DEBUG` is true; noted in the runbook's "Notes and known warnings".
