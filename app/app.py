# third-party imports
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    print(request.form)
    return redirect('/')
