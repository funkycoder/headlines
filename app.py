import datetime
import json
import feedparser
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
import urllib

app = Flask(__name__)

RSS_FEEDS = {'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             'vnexpress': 'https://vnexpress.net/rss/tin-moi-nhat.rss',
             'dantri': 'https://dantri.com.vn/trangchu.rss'}

DEFAULTS = {'publication': 'cnn',
            'city': 'London, UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=785f6ef1ac26c66cfe8dd3d110e0bb3c"

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=4e1b04781d834b7eb4aa731ecc0e79a9"


@app.route('/')
# @app.route('/<publication>')
# def get_news(publication='cnn'):
# def get_news():
def home():
    # Get customized headlines, based on user input or default
    publication = request.args.get("publication")
    publication, articles = get_news(publication)
    # Get customized weather, based on user input or default
    city = request.args.get("city")
    city, weather = get_weather(city)
    # Get customized currency, based on user input or default
    currency_from = request.args.get("currency_from")
    currency_to = request.args.get("currency_to")
    currency_from, currency_to, rate, currencies = get_rate(currency_from, currency_to)
    response = make_response(render_template("home.html",
                                             publication=publication,
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = get_value_fallback_cookie("publication")
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return publication, feed['entries']


def get_weather(query):
    if not query:
        city = get_value_fallback_cookie("city")
    else:
        city = query
    city = urllib.parse.quote(city)
    url = WEATHER_URL.format(city)
    # TODO: Catch 404 error here
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   "country": parsed["sys"]["country"]}
    return city, weather


def get_rate(currency_from, currency_to):
    if not currency_from:
        currency_from = get_value_fallback_cookie("currency_from")
    if not currency_to:
        currency_to = get_value_fallback_cookie("currency_to")
    data = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(data).get('rates')
    frm_rate = parsed.get(currency_from.upper())
    to_rate = parsed.get(currency_to.upper())
    return currency_from, currency_to, to_rate/frm_rate, parsed.keys()


def get_value_fallback_cookie(key):
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
