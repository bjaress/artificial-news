import behave as bhv
import data as d

@bhv.given("there is a simple news item about frogs")
def news_frogs(context):
    d.topics(context)["frogs"] = d.NewsItem(
        headline_html="""<a href='/wiki/Frog'>Something</a> happened.""",
        headline_plain="""Something happened.""",
        Frog=d.Article(
            markup="""A frog is a type of animal.""",
            plain="""A frog is a type of animal.""",
        ),
    )
    d.sync(context)
