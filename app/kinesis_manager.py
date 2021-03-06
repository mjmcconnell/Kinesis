# stdlib imports
import json
import time
from datetime import datetime

# third-party imports
import boto3


client = boto3.client('kinesis')


class KinesisStreamManager(object):

    @classmethod
    def _create_stream(cls, stream_name, shard_count, is_encrypted):
        try:
            client.create_stream(
                StreamName=stream_name,
                ShardCount=shard_count
            )
        except client.exceptions.ResourceInUseException:
            pass

    @classmethod
    def _enable_stream_encryption(cls, stream_name, encryption_type, key_id):
        return client.start_stream_encryption(
            StreamName=stream_name,
            EncryptionType=encryption_type,
            KeyId=key_id
        )

    @classmethod
    def _disable_stream_encryption(cls, stream_name, encryption_type, key_id):
        return client.stop_stream_encryption(
            StreamName=stream_name,
            EncryptionType=encryption_type,
            KeyId=key_id
        )

    @classmethod
    def _current_stream_status(cls, stream_name):
        stream_desc = client.describe_stream(StreamName=stream_name)
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
        request_kwargs = {'Limit': limit}
        if exclusive_start_stream_name:
            request_kwargs['ExclusiveStartStreamNam'] = exclusive_start_stream_name
        response = client.list_streams(**request_kwargs)
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
        return client.describe_stream(StreamName=stream_name)

    @classmethod
    def get_latest_records(cls, stream_name, shard_id, shard_it=None):
        if shard_it is None:
            shard_it = cls.get_current_iterator(stream_name, shard_id)

        try:
            return client.get_records(ShardIterator=shard_it)
        except client.exceptions.ExpiredIteratorException:
            return {
                'NextShardIterator': cls.get_current_iterator(stream_name, shard_id),
                'Records': [
                    'Iterator has expired, and buffer has been cleaner.',
                    'All records should now be in the S3 bucket'
                ]
            }

    @classmethod
    def get_current_iterator(cls, stream_name, shard_id):
        return client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='LATEST'
        )['ShardIterator']

    @classmethod
    def create(cls, stream_name, shard_count=1, is_encrypted=False):
        cls._create_stream(stream_name, shard_count, is_encrypted)
        if is_encrypted:
            cls.enable_encryption(stream_name)

    @classmethod
    def enable_encryption(cls, stream_name, encryption_type='KMS', key_id='alias/aws/kinesis'):
        while cls.get_status(stream_name) == 'CREATING':
            time.sleep(1)
        cls._enable_stream_encryption(stream_name, encryption_type, key_id)

    @classmethod
    def disable_encryption(cls, encryption_type='KMS', key_id='alias/aws/kinesis'):
        cls._disable_stream_encryption(encryption_type, key_id)

    @classmethod
    def get_status(cls, stream_name):
        return cls._current_stream_status(stream_name)

    @classmethod
    def list(cls, limit=10, exclusive_start_stream_name=None):
        return cls._list_streams(limit, exclusive_start_stream_name)

    @classmethod
    def describe(cls, stream_name):
        return cls._describe_stream(stream_name).get('StreamDescription')

    @classmethod
    def close(cls, stream_name):
        return client.delete_stream(StreamName=stream_name)

    @classmethod
    def load(cls, stream_name, num_users):
        """Populates the stream with user data.

        `put_record` sample response:
            {'SequenceNumber': '4959167...', 'ShardId': 'shardId-000000000000'}

        Returns the latest
        """
        for i in range(num_users):
            user = {
                'user': f'user {i}',
                'action': i,
                'timestamp': str(datetime.now())
            }
            client.put_record(
                StreamName=stream_name,
                Data=json.dumps(user),
                PartitionKey='partitionkey',
            )
