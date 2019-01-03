# stdlib imports
import urllib
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
    current_iterator = request.args.get('next_shard_it')

    records = []
    next_iterator = ''
    for stream_name in stream.list():
        stream_desc = stream.describe(stream_name)
        active_streams[stream_name] = stream_desc

        for shard in stream_desc['Shards']:
            latest_records = stream.get_latest_records(shard['ShardId'], current_iterator)
            next_iterator = latest_records['NextShardIterator']
            if latest_records['Records']:
                records.append(latest_records['Records'])

    return render_template('index.html', **{
        'active_streams': active_streams,
        'next_iterator': next_iterator,
        'records': records
    })


@app.route('/add', methods=['POST'])
def add():
    num_users = request.form.get('num_users', 0)
    next_shard_it = request.form.get('next_shard_it')
    print(f'CREATING {num_users} USER ACCOUNTS')
    stream.load(int(num_users))
    safe_next_shard_it = urllib.parse.quote_plus(next_shard_it)
    return redirect(f'/?next_shard_it={safe_next_shard_it}')
