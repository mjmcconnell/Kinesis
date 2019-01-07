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


def get_streams():
    streams = []
    for stream_name in stream.list():
        status = stream.describe(stream_name).get('StreamStatus')
        streams.append((stream_name, f'{stream_name} ({status})'))
    return streams


@app.route('/')
def index():
    shard_data = defaultdict(dict)
    shard_its = {k: v for k, v in request.args.items() if k.startswith('shardId')}

    active_stream_name = request.args.get('active_stream_name')

    if active_stream_name:
        stream_description = stream.describe(active_stream_name)
        for shard in stream_description['Shards']:
            latest_records = stream.get_latest_records(
                active_stream_name,
                shard['ShardId'],
                shard_its.get(shard['ShardId'])
            )
            if latest_records:
                shard_data[shard['ShardId']]['next_iterator'] = urllib.parse.quote_plus(
                    latest_records['NextShardIterator'])
                shard_data[shard['ShardId']]['records'] = latest_records['Records']

    return render_template('index.html', **{
        'streams': get_streams(),
        'active_stream_name': active_stream_name,
        'shard_data': shard_data,
    })


@app.route('/add_record', methods=['POST'])
def add_user():
    from datetime import datetime
    import requests
    host = ''
    body = {
        'user': f'user 1',
        'action': '0',
        'timestamp': str(datetime.now())
    }
    print(requests.post(host, data=body))
    return redirect('/')


@app.route('/add_records', methods=['POST'])
def add():
    shard_its = '&'.join([f'{k}={v}' for k, v in request.form.items() if k.startswith('shardId')])
    num_users = request.form.get('num_users', 0)
    stream_name = request.form.get('active_stream_name')

    stream.load(
        stream_name=stream_name,
        num_users=int(num_users)
    )
    return redirect(f'/?active_stream_name={stream_name}&{shard_its}')


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
