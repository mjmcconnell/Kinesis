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

    @classmethod
    def _enable_stream_encryption(cls, encryption_type, key_id):
        return client.start_stream_encryption(
            stream_name=KINESIS_STREAM_ID,
            encryption_type=encryption_type,
            key_id=key_id
        )

    @classmethod
    def _disable_stream_encryption(cls, encryption_type, key_id):
        return client.stop_stream_encryption(
            stream_name=KINESIS_STREAM_ID,
            encryption_type=encryption_type,
            key_id=key_id
        )

    @classmethod
    def _current_stream_status(cls):
        stream_desc = client.describe_stream(KINESIS_STREAM_ID)
        return stream_desc['StreamDescription']['StreamStatus']

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

    @classmethod
    def _describe_stream(cls, stream_name):
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
        return client.describe_stream(stream_name=stream_name)

    @classmethod
    def _watch_stream_shard(cls, shard_id):
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
        shard_it = cls.get_current_iterator()

        while True:
            out = client.get_records(shard_it, limit=50)
            shard_it = out['NextShardIterator']
            print(out)
            time.sleep(1)

    @classmethod
    def get_current_iterator(cls, shard_id):
        return client.get_shard_iterator(KINESIS_STREAM_ID, shard_id, 'LATEST')['ShardIterator']

    @classmethod
    def create(cls, shard_count=1):
        return cls._create_stream(shard_count)

    @classmethod
    def enable_encryption(cls, encryption_type='KMS', key_id='aws/kinesis'):
        cls._enable_stream_encryption(encryption_type, key_id)

    @classmethod
    def disable_encryption(cls, encryption_type='KMS', key_id='aws/kinesis'):
        cls._disable_stream_encryption(encryption_type, key_id)

    @classmethod
    def get_status(cls):
        return cls._current_stream_status()

    @classmethod
    def list(cls, limit=10, exclusive_start_stream_name=None):
        return cls._list_streams(limit, exclusive_start_stream_name)

    @classmethod
    def describe(cls, stream_name):
        return cls._describe_stream(stream_name).get('StreamDescription')

    @classmethod
    def watch(cls, shard_id):
        cls._watch_stream_shard(shard_id)

    @classmethod
    def close(cls):
        return print(client.delete_stream(KINESIS_STREAM_ID))

    @classmethod
    def load(cls, num_users):
        """Populates the stream with user data.

        `put_record` sample response:
            {'SequenceNumber': '4959167...', 'ShardId': 'shardId-000000000000'}

        Returns the latest
        """
        for i in range(num_users):
            user = {
                'name': f'user {i}',
                'address': f'address {i}'
            }
            client.put_record(KINESIS_STREAM_ID, json.dumps(user), 'partitionkey')
