import feedparser
from flask import Flask
from flask import render_template
from flask import request


app = Flask(__name__)

RSS_FEEDS = {'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}


@app.route('/')
# @app.route('/<publication>')
# def get_news(publication='cnn'):
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "cnn"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    # feed['entries'] is a list
    # first_article = feed['entries'][0]
    return render_template("home.html",
                           articles=feed['entries'])


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
