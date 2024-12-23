import os
import time
import requests

from types import SimpleNamespace

from steps.data import mp3 as mock_mp3

def before_all(context):
    prop = SimpleNamespace()
    mocks = []
    for key, value in os.environ.items():
        if key.startswith("prop."):
            include_in(prop, key.split(".")[1:], value)
        if key.endswith(".url") and not key.endswith("app.url"):
            mocks.append(value)
    context.prop = prop
    context.mocks = mocks
    poll(
        f"confirming app is up",
        200,
        lambda: requests.get(f"{context.prop.app.url}/health").status_code,
    )


def include_in(namespace, key_path, value):
    as_dict = namespace.__dict__
    first = key_path[0]
    if len(key_path) == 1:
        as_dict[first] = value
    else:
        if first not in as_dict:
            as_dict[first] = SimpleNamespace()
        include_in(as_dict[first], key_path[1:], value)


def before_scenario(context, scenario):
    for mock in context.mocks:
        poll(
            f"confirming/resetting {mock}",
            200,
            lambda: requests.post(f"{mock}/__admin/reset", timeout=0.01).status_code,
        )
    mock_mp3(context)


def poll(description, expected, action):
    exception = Exception(f"Exhausted attempts at {description}")
    result = None
    for attempt in range(300):
        try:
            result = action()
            if result == expected:
                # Behave cleverly intercepts logging and then shows it if, and
                # only if, there is a test failure.  We're using print() here to
                # bypass that and give actual progress updates.
                print(f"Attempt {attempt} at {description} succeeded.", flush=True)
                return result
            message = result
        except Exception as e:
            exception = e
            message = exception
        print(f"Attempt {attempt} at {description} failed with {message}.", flush=True)
        # exponential backoff, capped at around seven minutes
        time.sleep(0.01 * (2 ** min(12, attempt)))
        print(f"Trying again at {description}.", flush=True)

    raise (exception)
