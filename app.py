from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Regexp
import re

API_KEY = '48f8ba1a-2ee3-41e6-a472-e3de2de67f6e'
BASE_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/'

class WordForm(FlaskForm):
    avail_letters = StringField("Letters", validators= [
        Regexp(r'^[a-z]+$', message="must contain letters only")
    ])
    avail_pattern = StringField("Pattern")
    avail_numbers = StringField("Max Length", validators= [
        Regexp(r'^[0-9]+$', message="must contain numbers"),
        Regexp(r'^(1[0]|[3-9])$', message="length must be greater than 3 and less than 10")
    ])
    submit = SubmitField("Go")

csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form, name="CSCI 4131")


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    print("Is letters empty? ", form.avail_letters.data=="")
    print("Is numers empty? ", form.avail_numbers.data=="")
    if form.validate_on_submit() or form.avail_numbers.data == "" or form.avail_letters.data == "":
        letters = form.avail_letters.data
        if form.avail_numbers.data == "":
            maxLen = 15
        else:
            maxLen = int(form.avail_numbers.data)
    else:
        return render_template("index.html", form=form)

##    if form.avail_numbers.data == "":
##        maxLen = 15
##    else:
##        maxLen = len(letters) + 1

    print("Letters: ", letters)
    print("Max length: ", maxLen)
    
    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    for l in range(3,maxLen+1):
        for word in itertools.permutations(letters,l):
            w = "".join(word)
            if w in good_words:
                word_set.add(w)

    word_set = sorted(word_set)
    word_set = sorted(word_set, key=len)

    return render_template('wordlist.html',
        wordlist=word_set,
        name="CSCI 4131")




@app.route('/proxy')
def proxy(word):
    url = "%s/%s" % (BASE_URL, word)
    params = {"api_key": API_KEY}
    args = dict(request.args.items())

    format = args.pop('format', 'json')
    callback = args.pop("callback", "processJSONP")
    params.update(args)
    
    result = requests.get(url, params=params)
    if result.status_code != 200:
        return Response(response="{'error':'There was an error in the API.'}",
                        status=result.status_code, mimetype='application/javascript')
    
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp



