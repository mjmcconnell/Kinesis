# stdlib imports
import json
import time

# third-party imports
from boto import kinesis

# local imports
from config import KINESIS_REGION
from config import KINESIS_STREAM_ID


client = kinesis.connect_to_region(KINESIS_REGION)


class KinesisStreamManager(object):

    @classmethod
    def _create_stream(cls, shard_count):
        try:
            client.create_stream(
                stream_name=KINESIS_STREAM_ID,
                shard_count=shard_count
            )
        except kinesis.exceptions.ResourceInUseException:
            pass

        stream_desc = client.describe_stream(KINESIS_STREAM_ID)
        while stream_desc['StreamDescription']['StreamStatus'] == 'CREATING':
            print(stream_desc['StreamDescription']['StreamStatus'])
            time.sleep(2)

    @classmethod
    def _list_streams(cls, limit, exclusive_start_stream_name):
        """Method for listing all live streams for the active region.
        Lists streams in batchs of [limit], until all streams are fetched, due
        to limitations placed on the api endpoint.

        Parameters:
            limit (integer) -- The maximum number of streams to list.
            exclusive_start_stream_name (string) -- The name of the stream to start the list with.

        kinesis `list_streams` sample response:
            {
                'HasMoreStreams': False,
                'StreamNames': ['kinesis-sample']
            }
        """
        stream_names = []
        response = client.list_streams(
            limit=limit,
            exclusive_start_stream_name=exclusive_start_stream_name
        )
        stream_names += response['StreamNames']
        if response['HasMoreStreams']:
            stream_names += cls._list_streams(
                limit=limit,
                exclusive_start_stream_name=stream_names[-1]
            )

        return stream_names

    def _describe_stream(self, stream_name):
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
        return client.describe_stream(StreamName=stream_name)

    def _watch_stream_shard(shard_id):
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
        shard_it = client.get_shard_iterator(KINESIS_STREAM_ID, shard_id, 'LATEST')

        while True:
            out = client.get_records(shard_it['ShardIterator'], limit=2)
            shard_it = out['NextShardIterator']
            print(out)
            time.sleep(0.2)

    @classmethod
    def create(cls, shard_count=1):
        return cls._create_stream(shard_count)

    @classmethod
    def list(cls, limit=10, exclusive_start_stream_name=None):
        print(cls._list_streams(limit, exclusive_start_stream_name))

    @classmethod
    def describe(cls, stream_name):
        print(cls._describe_stream(stream_name))

    @classmethod
    def watch(cls, shard_id):
        cls._watch_stream_shard(shard_id)

    @classmethod
    def close(cls):
        return client.delete_stream(KINESIS_STREAM_ID)

    @classmethod
    def load(cls):
        """Populates the stream with user data.
        """
        for i in range(50):
            user = {
                'name': f'user {i}',
                'address': f'address {i}'
            }
            client.put_record(KINESIS_STREAM_ID, json.dumps(user), 'partitionkey')
