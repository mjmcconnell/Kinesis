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

    def __init__(self, _kinesis):
        try:
            _kinesis.create_stream(KINESIS_STREAM_ID, 1)
        except kinesis.exceptions.ResourceInUseException:
            pass

        self.desc = _kinesis.describe_stream(KINESIS_STREAM_ID)
        while self.desc['StreamDescription']['StreamStatus'] == 'CREATING':
            time.sleep(2)

    def start(self):
        for i in range(50):
            user = {
                'name': f'user {i}',
                'address': f'address {i}'
            }
            _kinesis.put_record(KINESIS_STREAM_ID, json.dumps(user), "partitionkey")

    def describe(self):
        print(self.desc)
        print(_kinesis.list_streams())

        # {'StreamDescription': {'EncryptionType': 'NONE', 'EnhancedMonitoring': [{'ShardLevelMetrics': []}], 'HasMoreShards': False, 'RetentionPeriodHours': 24, 'Shards': [], 'StreamARN': 'arn:aws:kinesis:eu-west-1:091595401634:stream/kinesis-sample', 'StreamCreationTimestamp': 1546442664.0, 'StreamName': 'kinesis-sample', 'StreamStatus': 'CREATING'}}
        # {'HasMoreStreams': False, 'StreamNames': ['kinesis-sample']}


def watch():
    shard_id = 'shardId-000000000000'   #we only have one shard!
    shard_it = _kinesis.get_shard_iterator(KINESIS_STREAM_ID, shard_id, "LATEST")["ShardIterator"]

    while True:
        out = _kinesis.get_records(shard_it, limit=2)
        shard_it = out["NextShardIterator"]
        print(out)
        time.sleep(0.2)
        # {u'Records': [{u'PartitionKey': u'partitionkey', u'Data': u'{"lastname": "Rau", "age": 23, "firstname": "Peyton", "gender": "male"}', u'SequenceNumber': u'49547280908463336004254488250517179461390244620594577410'}, {u'PartitionKey': u'partitionkey', u'Data': u'{"lastname": "Mante", "age": 29, "firstname": "Betsy", "gender": "male"}', u'SequenceNumber': u'49547280908463336004254488250518388387209859249769283586'}], u'NextShardIterator': u'AAAAAAAAAAEvI7MPAuwLucWMwYtZnATetztUUTqgtQaTaihyV/+buCmSqBdKnAwv2dMNeGlYo3fvYCcH6aI/A+DtG3uq+MnG8AlyrX7UrHnlX5OF0xG/IEhSJyyToPvwtJ8odDoWShib3bjuk+944QcsPrRRsUsBNx6xyKgnY+xi9lXvweiImL1ByK5Bdj0sLoRp/9nBWfw='}


def close():
    print('############ CLOSING STREAM')
    _kinesis.delete_stream(KINESIS_STREAM_ID)


if __name__ == "__main__":
    print('############ CREATING NEW STREAM')
    stream = KinesisStream(_kinesis)
    try:
        print('############ NEW STREAM DESC')
        stream.describe()
        print('############ STARTING POPULATING')
        stream.start()
    except Exception as e:
        print(e)
