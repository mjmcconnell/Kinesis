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
    next_iterator = ''
    shard_records = defaultdict(list)

    current_iterator = request.args.get('next_shard_it')
    active_stream_name = request.args.get('active_stream_name')

    if active_stream_name:
        stream_description = stream.describe(active_stream_name)
        for shard in stream_description['Shards']:
            latest_records = stream.get_latest_records(
                active_stream_name,
                shard['ShardId'],
                current_iterator
            )
            if latest_records:
                next_iterator = latest_records['NextShardIterator']
                shard_records[shard['ShardId']] = latest_records['Records']

    return render_template('index.html', **{
        'streams': get_streams(),
        'active_stream_name': active_stream_name,
        'current_iterator': urllib.parse.quote_plus(current_iterator) if current_iterator else '',
        'next_iterator': urllib.parse.quote_plus(next_iterator),
        'shard_records': shard_records,
    })


@app.route('/add_records', methods=['POST'])
def add():
    num_users = request.form.get('num_users', 0)
    next_shard_it = request.form.get('next_shard_it')
    active_stream_name = request.form.get('active_stream_name')

    print(f'CREATING {num_users} USER ACCOUNTS')
    stream.load(
        stream_name=active_stream_name,
        num_users=int(num_users)
    )
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
