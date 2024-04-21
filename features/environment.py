import os
import time
import requests

from types import SimpleNamespace


def before_all(context):
    prop = SimpleNamespace()
    mocks = []
    for key, value in os.environ.items():
        if key.startswith("prop."):
            include_in(prop, key.split(".")[1:], value)
        if key.endswith(".url"):
            mocks.append(value)
    context.prop = prop
    context.mocks = mocks
    poll(f"confirming app is up",
         200,
         lambda: requests.get(f"{context.prop.app.url}/health").status_code)

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
    mocks = [ context.prop.wikipedia.url
            , context.prop.spreaker.url
            , context.prop.google.url ]
    for mock in mocks:
        poll(f"confirming/resetting {mock}",
             200,
             lambda: requests.post(f"{mock}/__admin/reset", timeout=0.01).status_code)

def poll(description, expected, action):
    exception = Exception(f"Exhausted attempts at {description}")
    result = None
    for attempt in range(300):
        print(f"Attempt {attempt} at {description}.", flush=True)
        try:
            result = action()
            if result == expected:
                return result
            print(result)
        except Exception as e:
            exception = e
            print(exception)
        time.sleep(1)
    raise(exception)
