from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import config
import requests
import operator
import re
import nltk
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "POST":
        try:
            url = request.form['url']
            req = requests.get(url)
            print(req.text)
        except:
            errors.append("Unable to get URL")
        if req:
            raw = BeautifulSoup(req.text, 'html.parser').get_text()
            nltk.data.path.append('../nltk_data')
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            results = sorted(no_stop_words_count.items(), key=operator.itemgetter(1), reverse=True)
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                pass
    return render_template('index.html', errors=errors, results=results)

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__=='__main__':
    app.run()
#print(os.environ['APP_SETTINGS'])