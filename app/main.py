# stdlib imports
import json
import time

# third-party imports
from boto import kinesis

# local imports
from config import KINESIS_REGION
from config import KINESIS_STREAM_ID


_kinesis = kinesis.connect_to_region(KINESIS_REGION)


class KinesisStream(object):

    def __init__(self, shard_count=1):
        """
        Parameters:
            shard_count:
                Type: Integer (1-100000)
                Desc:
                    The number of shards that the stream will use. The
                    throughput of the stream is a function of the number of
                    shards; more shards are required for greater provisioned
                    throughput.
        """
        try:
            resp = _kinesis.create_stream(
                StreamName=KINESIS_STREAM_ID,
                ShardCount=shard_count
            )
            print(resp)
        except kinesis.exceptions.ResourceInUseException:
            pass

        stream_desc = _kinesis.describe_stream(KINESIS_STREAM_ID)
        while stream_desc['StreamDescription']['StreamStatus'] == 'CREATING':
            print(stream_desc['StreamDescription']['StreamStatus'])
            time.sleep(2)

    def start(self):
        """Populates the stream with user data.
        """
        for i in range(50):
            user = {
                'name': f'user {i}',
                'address': f'address {i}'
            }
            _kinesis.put_record(KINESIS_STREAM_ID, json.dumps(user), "partitionkey")

    @classmethod
    def _list_streams(cls, limit=10, exclusive_start_stream_name=None):
        """Method for listing all live streams for the active region.
        Lists streams in batchs of [limit], until all streams are fetched, due
        to limitations placed on the api endpoint.

        Parameters:
            Limit (integer) -- The maximum number of streams to list.
            ExclusiveStartStreamName (string) -- The name of the stream to start the list with.

        `list_streams` sample response:
            {
                'HasMoreStreams': False,
                'StreamNames': ['kinesis-sample']
            }
        """
        stream_names = []
        response = _kinesis.list_streams(
            Limit=limit,
            ExclusiveStartStreamName=exclusive_start_stream_name
        )
        stream_names += response['StreamNames']
        if response['HasMoreStreams']:
            stream_names += cls._list_streams(
                exclusive_start_stream_name=stream_names[-1]
            )

        return stream_names

    def describe(self):
        """
        Desc sample output:
            {
                'StreamDescription': {
                    'EncryptionType': 'NONE',
                    'EnhancedMonitoring': [{
                        'ShardLevelMetrics': []
                    }],
                    'HasMoreShards': False,
                    'RetentionPeriodHours': 24,
                    'Shards': [],
                    'StreamARN': 'arn:aws:kinesis:eu-west-1:091595401634:stream/kinesis-sample',
                    'StreamCreationTimestamp': 1546442664.0,
                    'StreamName': 'kinesis-sample',
                    'StreamStatus': 'CREATING'
                }
            }

        """
        streams = self._list_streams()
        print(streams)

        for stream_name in streams['StreamNames']:
            stream_desc = _kinesis.describe_stream(StreamName=stream_name)
            print(stream_desc)


def watch(shard_id='shardId-000000000000'):
    """Outputs the current data within a given shard (shard_id) every 0.2 seconds.
    Sample output:
        {
            'Records': [{
                'PartitionKey': 'partitionkey',
                'Data': '{"lastname": "Rau", "age": 23, "firstname": "Peyton", "gender": "male"}',
                'SequenceNumber': '(int)'
            }, ...],
            'NextShardIterator': '(str)'
        }
    """
    shard_it = _kinesis.get_shard_iterator(KINESIS_STREAM_ID, shard_id, "LATEST")["ShardIterator"]

    while True:
        out = _kinesis.get_records(shard_it, limit=2)
        shard_it = out["NextShardIterator"]
        print(out)
        time.sleep(0.2)


def close():
    """Removes the active stream from AWS."""
    print('############ CLOSING STREAM')
    _kinesis.delete_stream(KINESIS_STREAM_ID)


if __name__ == "__main__":
    print('############ CREATING NEW STREAM')
    stream = KinesisStream()
    try:
        print('############ STREAM DESC')
        stream.describe()
        print('############ STARTING POPULATING')
        stream.start()
        print('############ STREAM DESC')
        stream.describe()
    except Exception as e:
        print(e)
