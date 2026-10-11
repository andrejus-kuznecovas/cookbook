"""Deploy the app to PythonAnywhere after CI passes.

Runs the update commands (git pull, pip install, migrate, collectstatic)
in a PythonAnywhere bash console via the API, then reloads the web app.

Required environment variables:
  PA_API_TOKEN   PythonAnywhere API token (GitHub secret)
  PA_USER        PythonAnywhere username
  PA_CONSOLE_ID  id of an existing, started bash console

Note: the PythonAnywhere API can only send input to a console that has
been started by opening it in a browser at least once. If the console
process has died (e.g. after PythonAnywhere server maintenance), this
script fails with instructions to reopen it.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

PA_USER = os.environ["PA_USER"]
PA_API_TOKEN = os.environ["PA_API_TOKEN"]
PA_CONSOLE_ID = os.environ["PA_CONSOLE_ID"]
DOMAIN = f"{PA_USER}.pythonanywhere.com"
BASE = f"https://www.pythonanywhere.com/api/v0/user/{PA_USER}"

UPDATE_COMMAND = (
    "workon cookbook && cd ~/cookbook && git pull --ff-only"
    " && pip install -r requirements.txt -q"
    " && python manage.py migrate --noinput"
    " && python manage.py collectstatic --noinput"
)


def api(method, path, payload=None, form=None):
    data = None
    headers = {"Authorization": f"Token {PA_API_TOKEN}"}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = form.encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(
        BASE + path, data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def fail(message):
    print(f"DEPLOY FAILED: {message}")
    sys.exit(1)


def run_update():
    marker = str(int(time.time()))
    sentinel = f"__DEPLOY_{marker}__"
    # Bash concatenates the quoted parts, so the echoed command line does
    # not contain the literal sentinel we poll for.
    command = f'{UPDATE_COMMAND}; echo __DEP\'\'LOY_{marker}__:$?\n'

    status, body = api(
        "POST", f"/consoles/{PA_CONSOLE_ID}/send_input/", payload={"input": command}
    )
    if status == 412:
        fail(
            "the deploy console is not running. Open "
            f"https://www.pythonanywhere.com/user/{PA_USER}/consoles/{PA_CONSOLE_ID}/"
            " in a browser once to restart it, then re-run this job."
        )
    if status != 200:
        fail(f"send_input returned HTTP {status}: {body}")

    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(10)
        status, body = api("GET", f"/consoles/{PA_CONSOLE_ID}/get_latest_output/")
        if status != 200:
            continue
        output = json.loads(body).get("output", "")
        if f"{sentinel}:" in output:
            idx = output.rfind(f"{sentinel}:")
            exit_code = output[idx + len(sentinel) + 1 :].split()[0].strip()
            tail = output[max(0, idx - 2500) : idx]
            print(tail)
            if exit_code != "0":
                fail(f"update commands exited with code {exit_code}")
            print("Update commands completed successfully.")
            return
    fail("timed out waiting for the update commands to finish")


def reload_webapp():
    for attempt in range(3):
        status, body = api("POST", f"/webapps/{DOMAIN}/reload/", form="")
        if status == 200:
            print("Web app reloaded.")
            return
        print(f"reload attempt {attempt + 1} returned HTTP {status}: {body}")
        time.sleep(65)  # API rate limit window
    fail("could not reload the web app")


def smoke_check():
    request = urllib.request.Request(f"https://{DOMAIN}/accounts/login/")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request) as resp:
                if resp.status == 200:
                    print("Smoke check passed: login page returns 200.")
                    return
        except urllib.error.HTTPError as err:
            print(f"smoke check attempt {attempt + 1}: HTTP {err.code}")
        time.sleep(10)
    fail("login page did not return 200 after reload")


if __name__ == "__main__":
    run_update()
    reload_webapp()
    smoke_check()
    print(f"Deployed to https://{DOMAIN}/")
