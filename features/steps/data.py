import behave as bhv

import requests
import time
import random


class NewsItem:
    def __init__(self, headline_html, headline_plain):
        self.headline_html = headline_html
        self.headline_plain = headline_plain
        self.articles = {}


class Article:
    def __init__(self, markup, plain):
        self.markup = markup
        self.plain = plain
        self.id = random.randint(1, 2**30)


def headline(context, topic, *args):
    if not hasattr(context, "topics"):
        context.topics = {}
    item = NewsItem(*args)
    context.topics[topic] = item
    return item.articles


@bhv.given("there is a news item about frogs")
def news_frogs(context):
    articles = headline(
        context,
        "frogs",
        """<a href=''>Something</a> happened.""",
        """Something happened.""",
    )
    articles["Frog"] = Article(
        """A frog is a type of animal.""", """A frog is a type of animal."""
    )
    sync(context)

def sync(context):
    pass #TODO
