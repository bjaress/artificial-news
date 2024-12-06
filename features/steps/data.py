import behave as bhv

import requests
import time
import random

SHOW_ID = 1234
BASE_64_MP3 = "Zm9v"


@bhv.when("it is time to generate news")
def trigger_app(context):
    response = requests.post(context.prop.app.url, json= {
      "message": {
        "attributes": {
          "spreaker_url": context.prop.spreaker.url,
          "spreaker_token": "DUMMY_TOKEN",
          "spreaker_show_id": SHOW_ID,
          "spreaker_title_limit": context.prop.spreaker.title_limit,
          "spreaker_age_limit": 30,
          "tts_api_key": "DUMMY_KEY",
          "tts_server": context.prop.google.url,
          "tts_length_limit": 300,
          "tts_intro": "INTRO",
          "tts_outro": "OUTRO",
          "wikipedia_url": context.prop.wikipedia.url,
          "wikipedia_headlines_page": "Template:In_the_news"
        },
        "messageId": "blahblah"
      },
      "subscription": "blah/blah/blah"
    })
    response.raise_for_status()

@bhv.then("headlines are retrieved from Wikipedia")
def headline_fetch(context):
    response = requests.post(
        f"{context.prop.wikipedia.url}/__admin/requests/find",
        json={
            "method": "GET",
            "urlPath": "/w/api.php",
            "queryParameters": {
                "action": {"equalTo": "parse"},
                "format": {"equalTo": "json"},
                "prop": {"equalTo": "text"},
                "page": {"equalTo": "Template:In_the_news"},
                "section": {"equalTo": "0"},
            },
        },
    )
    response.raise_for_status()
    assert len(response.json()["requests"]) == 1, response.json()

@bhv.then("the episode list from Spreaker is retrieved")
def episode_fetches(context):
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/requests/find",
        json={
            "method": "GET",
            'urlPath': f"/v2/shows/{SHOW_ID}/episodes",
            "queryParameters": {
                "filter": {"equalTo": "editable"},
                "sorting": {"equalTo": "oldest"},
            },
        },
    )
    response.raise_for_status()
    reqs = response.json()["requests"]
    assert len(reqs) == 1, response.json()
    assert reqs[0]['headers']["Authorization"] == "Bearer DUMMY_TOKEN"

@bhv.then("Wikipedia articles about {topic} are retrieved")
def article_fetches(context, topic):
    for title in context.topics[topic].articles:
        response = requests.post(
            f"{context.prop.wikipedia.url}/__admin/requests/find",
            json={
                "urlPath": f"/w/rest.php/v1/page/{title}",
            },
        )
        response.raise_for_status()
        assert len(response.json()["requests"]) == 1, (response.json(), title)

def sync(context):
    sync_headlines(context)
    sync_articles(context)
    sync_existing_episodes(context)

def sync_existing_episodes(context):
    items = [ { 'title': title
              , 'published_at': '2000-01-01 00:00:00'
              , 'episode_id': id
              } for id, title in enumerate(episodes(context))]
    data = {
        'request': {
            'urlPath': f"/v2/shows/{SHOW_ID}/episodes",
        },
        'response': {
            'status': 200,
            'jsonBody': {
                'response': {
                    'items': items
                },
            },
        },
    }
    response = requests.post(
        f"{context.prop.spreaker.url}/__admin/mappings", json=data
    )
    response.raise_for_status()

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
                        'latest': {'id': article.id},
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
    return f"<div><ul><li>{inner}</li></ul></div>"



def topics(context):
    if not hasattr(context, "topics"):
        context.topics = {}
    return context.topics

def episodes(context):
    if not hasattr(context, "episodes"):
        context.episodes = []
    return context.episodes

def mp3(context):
    data = {
        "request": {
            "urlPath": "/v1/text:synthesize"
        },
        "response": {
            "status": 200,
            "jsonBody": {
                "audioContent": BASE_64_MP3
            },
        },
    }
    response = requests.post(
        f"{context.prop.google.url}/__admin/mappings", json=data
    )
    response.raise_for_status()

class NewsItem:
    def __init__(self, headline_html, headline_plain, **articles):
        self.headline_html = headline_html
        self.headline_plain = headline_plain
        self.articles = articles


class Article:
    def __init__(self, markup, plain):
        self.markup = markup
        self.plain = plain
        self.id = str(random.randint(1, 2**30))
