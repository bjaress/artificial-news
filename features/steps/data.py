import behave as bhv

import requests
import time
import random


@bhv.given("there is a simple news item about frogs")
def news_frogs(context):
    topics(context)["frogs"] = NewsItem(
        headline_html="""<a href='/wiki/Frog'>Something</a> happened.""",
        headline_plain="""Something happened.""",
        Frog=Article(
            markup="""A frog is a type of animal.""",
            plain="""A frog is a type of animal.""",
        ),
    )
    sync(context)


def sync(context):
    sync_headlines(context)
    sync_articles(context)

def sync_articles(context):
    for news_item in context.topics.values():
        for title, article in news_item.articles.items():
            data = {
                'request': {
                    'urlPath': f"/w/rest.php/v1/page/{title}"
                },
                'response': {
                    'status': 200,
                    'jsonBody': {
                        'latest': article.id,
                        'source': article.markup
                    },
                }
            }
            response = requests.post(
                f"{context.prop.wikipedia.url}/__admin/mappings", json=data
            )
            response.raise_for_status()

def sync_headlines(context):
    data = {
        "request": {
            "urlPath": "/w/api.php",
            "queryParameters": {"page": {"equalTo": "Template:In_the_news"}},
        },
        "response": {
            "status": 200,
            "jsonBody": {
                "parse": {
                    "title": "Template:In the news",
                    "pageid": 482256,
                    "text": {"*": headlines_html(context)},
                }
            },
        },
    }
    response = requests.post(
        f"{context.prop.wikipedia.url}/__admin/mappings", json=data
    )
    response.raise_for_status()


def headlines_html(context):
    inner = "</li><li>".join(item.headline_html for item in context.topics.values())
    return f"<div><ul><li></li></ul></div>"


def topics(context):
    if not hasattr(context, "topics"):
        context.topics = {}
    return context.topics


class NewsItem:
    def __init__(self, headline_html, headline_plain, **articles):
        self.headline_html = headline_html
        self.headline_plain = headline_plain
        self.articles = articles


class Article:
    def __init__(self, markup, plain):
        self.markup = markup
        self.plain = plain
        self.id = random.randint(1, 2**30)
