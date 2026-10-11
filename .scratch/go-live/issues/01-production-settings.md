# 01: Production-safe settings and static files

**What to build:** The app runs correctly with production settings: secrets
and hosts come from the environment, static files are collected and served
without the dev server, and a developer with no env vars set still gets a
working `runserver` out of the box.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` are read from environment variables in `config/settings.py`, with the current dev values as defaults (`DEBUG` defaults to true; env value "False"/"0" disables it)
- [x] WhiteNoise is added (requirements + middleware) and `STATIC_ROOT` is configured; `python manage.py collectstatic --noinput` completes cleanly
- [x] With `DEBUG=False` and `ALLOWED_HOSTS` set, `python manage.py check --deploy` reports no SECRET_KEY/DEBUG errors
- [x] Tests cover the env-var override behavior
- [x] Existing 14 tests still pass
