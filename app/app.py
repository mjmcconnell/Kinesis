# stdlib imports
from collections import defaultdict

# third-party imports
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request

# local imports
from kinesis_manager import KinesisStreamManager


app = Flask(__name__)
stream = KinesisStreamManager()
stream.create()


@app.route('/')
def index():
    active_streams = defaultdict(dict)
    for stream_name in stream.list():
        active_streams[stream_name] = stream.describe(stream_name)

    return render_template('index.html', **{
        'active_streams': active_streams
    })


@app.route('/add', methods=['POST'])
def add():
    num_users = request.form.get('num_users', 0)
    print('CREATING {num_users} USER ACCOUNTS')
    stream.create(int(num_users))
    return redirect('/')
