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
    current_iterators = defaultdict(list)
    for stream_name in stream.list():
        stream_desc = stream.describe(stream_name)
        active_streams[stream_name] = stream_desc

        for shard in stream_desc['Shards']:
            current_iterators[stream_name].append(
                stream.get_current_iterator(shard['ShardId'])
            )

    return render_template('index.html', **{
        'active_streams': active_streams,
        'current_iterators': current_iterators
    })


@app.route('/add', methods=['POST'])
def add():
    num_users = request.form.get('num_users', 0)
    print(f'CREATING {num_users} USER ACCOUNTS')
    stream.load(int(num_users))
    return redirect('/')
