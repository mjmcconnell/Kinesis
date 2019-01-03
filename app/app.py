# stdlib imports
import json

# third-party imports
from flask import Flask
from flask import render_template
from flask import request


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    return json.dumps(request.form)
