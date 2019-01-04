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
# stream.create()


def get_streams():
    streams = []
    for stream_name in stream.list():
        status = stream.describe(stream_name).get('StreamStatus')
        streams.append((stream_name, f'{stream_name} ({status})'))
    return streams


@app.route('/')
def index():
    active_streams = defaultdict(dict)
    current_iterator = request.args.get('next_shard_it')
    active_stream_name = request.args.get('active_stream_name')

    records = []
    next_iterator = ''
    # for stream_name in stream.list():
    #     stream_desc = stream.describe(stream_name)
    #     active_streams[stream_name] = stream_desc

    #     for shard in stream_desc['Shards']:
    #         latest_records = stream.get_latest_records(shard['ShardId'], current_iterator)
    #         if latest_records:
    #             next_iterator = latest_records['NextShardIterator']
    #             if latest_records['Records']:
    #                 records = latest_records['Records']

    return render_template('index.html', **{
        'streams': get_streams(),
        'active_streams': active_streams,
        'active_stream_name': active_stream_name,
        'current_iterator': urllib.parse.quote_plus(current_iterator) if current_iterator else '',
        'next_iterator': urllib.parse.quote_plus(next_iterator),
        'records': records
    })


@app.route('/add', methods=['POST'])
def add():
    num_users = request.form.get('num_users', 0)
    next_shard_it = request.form.get('next_shard_it')
    active_stream_name = request.form.get('active_stream_name')

    print(f'CREATING {num_users} USER ACCOUNTS')
    stream.load(int(num_users))
    return redirect(f'/?next_shard_it={next_shard_it}')


@app.route('/set_stream', methods=['POST'])
def set_stream():
    stream_name = request.form.get('stream_name')
    new_stream_name = request.form.get('new_stream_name')
    shard_count = request.form.get('shard_count')
    is_encrypted = request.form.get('is_encrypted')

    if new_stream_name:
        stream_name = new_stream_name
        stream.create(
            stream_name=stream_name,
            shard_count=int(shard_count),
            is_encrypted=int(is_encrypted)
        )

    return redirect(f'/?active_stream_name={stream_name}')
