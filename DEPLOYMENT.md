# Deploying Cookbook to PythonAnywhere

This runbook takes you from nothing to a live, login-protected app at
`https://<username>.pythonanywhere.com`, on PythonAnywhere's free tier.
The production database is the same SQLite file used in development,
living on PythonAnywhere's persistent disk (see
[ADR-0002](docs/adr/0002-sqlite-in-production.md)).

Wherever you see `<username>`, substitute your PythonAnywhere username.
Commands shown in `bash` blocks run in a PythonAnywhere **Bash console**
(Consoles tab).

## Going live

1. **Create a PythonAnywhere account.** Go to
   [www.pythonanywhere.com](https://www.pythonanywhere.com), choose
   **Create a Beginner account** (free, no card). Pick the username with
   care: the app's URL will be `https://<username>.pythonanywhere.com`.
   New accounts get the "innit" system image, which provides Python 3.13
   — the same version used in development. (Django 6.1 requires Python ≥
   3.12; you can confirm your image under Account → System image.)

2. **Open a Bash console** from the Consoles tab.

3. **Clone the repo:**

   ```bash
   git clone https://github.com/andrejus-kuznecovas/cookbook.git
   cd cookbook
   ```

4. **Create a virtualenv with Python 3.13 and install dependencies:**

   ```bash
   mkvirtualenv cookbook --python=python3.13
   pip install -r requirements.txt
   ```

   `mkvirtualenv` is pre-installed on PythonAnywhere; it creates the env
   at `/home/<username>/.virtualenvs/cookbook` and activates it (your
   prompt shows `(cookbook)`). In later console sessions, reactivate it
   with `workon cookbook`.

5. **Create the database schema:**

   ```bash
   python manage.py migrate
   ```

   This creates `/home/<username>/cookbook/db.sqlite3` on the persistent
   disk. (Console commands run fine without the production env vars; the
   settings' development defaults apply and are harmless here.)

6. **Create both partner accounts** — run this twice, once per partner:

   ```bash
   python manage.py createsuperuser
   python manage.py createsuperuser
   ```

   Alternatively, create just your own account now and add your
   partner's later in the Django admin (`/admin` → Users → Add); a
   regular user is enough for the app, superuser is only needed for
   admin access.

7. **Generate a production `SECRET_KEY`** and copy the output — you
   paste it into the WSGI file in step 10:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

8. **Create the web app.** On the **Web** tab click **Add a new web
   app**, confirm the domain `<username>.pythonanywhere.com`, choose
   **Manual configuration** (not "Django" — that would scaffold a new
   project), and select **Python 3.13**.

9. **Point the web app at your code and virtualenv.** Still on the Web
   tab:
   - **Source code:** `/home/<username>/cookbook`
   - **Virtualenv:** `/home/<username>/.virtualenvs/cookbook`

10. **Edit the WSGI configuration file.** The Web tab links to it
    (`/var/www/<username>_pythonanywhere_com_wsgi.py`). Replace its
    entire contents with the snippet below, filling in `<username>` and
    the key from step 7. The environment variables must be set in this
    file, before Django loads, because PythonAnywhere's free tier has no
    other place to define per-app env vars for the web worker.

    ```python
    import os
    import sys

    # Project directory (where manage.py lives).
    path = '/home/<username>/cookbook'
    if path not in sys.path:
        sys.path.insert(0, path)

    # Production configuration, read by config/settings.py.
    # Must be set before get_wsgi_application() imports the settings.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    os.environ['SECRET_KEY'] = '<paste the key from step 7>'
    os.environ['DEBUG'] = 'False'
    os.environ['ALLOWED_HOSTS'] = '<username>.pythonanywhere.com'

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    ```

    This mirrors the repo's `config/wsgi.py` (settings module
    `config.settings`) and uses exactly the variable names
    `config/settings.py` reads: `SECRET_KEY`, `DEBUG` (any of
    `0/false/no/off` means off), and `ALLOWED_HOSTS` (comma-separated
    list; one host is enough here).

11. **Collect static files.** Back in the Bash console:

    ```bash
    workon cookbook
    cd ~/cookbook
    python manage.py collectstatic --noinput
    ```

    This fills `/home/<username>/cookbook/staticfiles` (the repo's
    `STATIC_ROOT`), including the hashed-manifest files WhiteNoise
    serves in production.

12. **Map static files.** On the Web tab, under **Static files**, add:
    - **URL:** `/static/`
    - **Directory:** `/home/<username>/cookbook/staticfiles`

    (WhiteNoise could serve these itself, but the mapping lets
    PythonAnywhere's web server serve them directly, which is faster and
    doesn't consume your CPU allowance.)

13. **Reload** the app with the green **Reload** button on the Web tab.

14. **Smoke-check the live app:**
    1. Open `https://<username>.pythonanywhere.com` in a private window
       — you should be redirected to the login page
       (`/accounts/login/`), not see any content.
    2. Log in with the first account — the meal-planning page loads with
       styling intact (if it looks unstyled, recheck steps 11–12).
    3. Add a recipe at `/recipes/new/` and save it.
    4. On the planning page, mark one of the next days as a Cooking Day.
    5. Select the new recipe and open `/shopping-list/` — its
       ingredients appear.
    6. Log out, then log in as the second partner (ideally on the other
       phone): the same recipe, the marked Cooking Day, and the shopping
       list are all visible.

> **Keep-alive:** free-tier web apps expire after one month of no owner
> activity. Click the **Run until ... (extend)** button on the Web tab
> when you visit, or when PythonAnywhere emails you a reminder.

## Updating the app

**Automatic (the normal path):** every push to `main` runs CI, and when
the tests pass, the `deploy` job in `.github/workflows/ci.yml` updates
PythonAnywhere automatically: it runs `git pull`, `pip install`,
`migrate`, and `collectstatic` in the deploy console via the
PythonAnywhere API, reloads the web app, and smoke-checks the login
page. It needs the `PA_API_TOKEN` repository secret and an existing
started bash console (id in the workflow). If the deploy job ever fails
with "console is not running" (can happen after PythonAnywhere server
maintenance), open the console once in a browser and re-run the job.

**Manual (fallback):** after new commits land on `main`:

```bash
workon cookbook
cd ~/cookbook
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then press **Reload** on the Web tab. (Only `git pull` and Reload are
strictly needed for template/code-only changes, but running all four is
always safe.)

## Backups

Per [ADR-0002](docs/adr/0002-sqlite-in-production.md), the backup story
is: download the database file. On the **Files** tab, browse to
`/home/<username>/cookbook/` and download `db.sqlite3` to your computer.
Do this after adding recipes you'd hate to lose. To restore, upload the
file back to the same place (overwriting) and Reload the app.

## Notes and known warnings

- **Deploy check.** With the production env vars set,
  `python manage.py check --deploy` reports no errors — only four
  security *warnings* (HSTS, SSL redirect, secure session/CSRF cookie).
  These are acceptable for this two-user app; HTTPS hardening beyond
  what PythonAnywhere provides by default is out of scope. Just use the
  `https://` URL on your phones.
- **Mail backend.** Django 6's deploy check (`mail.E001`) rejects the
  development-only console email backend. Since the app sends no email,
  `config/settings.py` only enables the console backend when
  `DEBUG=True`; in production Django's default SMTP backend applies and
  is never used. No email configuration is needed on PythonAnywhere.
