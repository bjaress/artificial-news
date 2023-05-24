import fastapi as fa
import typing as tp
import datetime as dt
import os

from api import tts
from api import spreaker
from api import models
from api import wikipedia
import api.editing
import logging

app = fa.FastAPI()
logging.basicConfig(level=logging.DEBUG)

# Converts models.NewsTrigger to models.Config
# Does not assume field names, but does assume a naming convention with
# two-part names.
def decompose_attributes(trigger: models.NewsTrigger):
    attributes = trigger.message.attributes
    parts = {}
    for name, structure in models.Config.__fields__.items():
        subparts = {}
        constructor = structure.type_
        for subname in constructor.__fields__.keys():
            subparts[subname] = getattr(attributes, f"{name}_{subname}")
        parts[name] = constructor(**subparts)
    return models.Config(**parts)


class Clients:
    def __init__(
        self, config: tp.Annotated[models.Config, fa.Depends(decompose_attributes)]
    ):
        self.wikipedia = wikipedia.Client(config.wikipedia)
        self.tts = tts.Client(config.tts)
        self.spreaker = spreaker.Client(config.spreaker)


@app.post("/")
def generate_news_external(clients: tp.Annotated[Clients, fa.Depends(Clients)]):
    generate_news(clients, api.editing)


def generate_news(clients, editing):
    headlines = clients.wikipedia.headlines()
    fresh_headline = clients.spreaker.fresh_headline(headlines)

    if fresh_headline is None:
        return {}

    plan = editing.extract_plan(clients.wikipedia, fresh_headline)
    clients.spreaker.upload(
        title=fresh_headline.text,
        audio=clients.tts.speak(plan.text()),
    )

    return {}


def cleanup_client(trigger: models.CleanupTrigger):
    return spreaker.Client(trigger.message.attributes)


@app.post("/cleanup")
def cleanup(spreaker: tp.Annotated[spreaker.Client, fa.Depends(cleanup_client)]):
    return spreaker.cleanup(today())


def today():
    if "TODAY" in os.environ:
        return dt.datetime.fromisoformat(os.environ["TODAY"])
    else:
        return dt.datetime.now()


@app.get("/health")
def health():
    return True
