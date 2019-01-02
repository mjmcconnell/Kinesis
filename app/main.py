# stdlib imports
import json
import time

# third-party imports
from boto import kinesis

# local imports
from config import KINESIS_REGION
from config import KINESIS_STREAM_ID
from models import User


class KinesisStream(object):

    def __init__(self, kinesis):
        self.stream = kinesis.create_stream(KINESIS_STREAM_ID, 1)

    def start(self):
        for user in User().generate(50):
            kinesis.put_record(KINESIS_STREAM_ID, json.dumps(user), "partitionkey")

    def describe(self):
        kinesis.describe_stream(KINESIS_STREAM_ID)
        # {u'StreamDescription': {u'HasMoreShards': False, u'StreamStatus': u'CREATING', u'StreamName': u'BotoDemo', u'StreamARN': u'arn:aws:kinesis:eu-west-1:374311255271:stream/BotoDemo', u'Shards': []}}
        kinesis.list_streams()
        # {u'StreamNames': [u'BotoDemo', u'IoTSensorDemo'], u'HasMoreStreams': False}


def watch(kinesis, stream):
    shard_id = 'shardId-000000000000'   #we only have one shard!
    shard_it = kinesis.get_shard_iterator(KINESIS_STREAM_ID, shard_id, "LATEST")["ShardIterator"]

    while True:
        out = kinesis.get_records(shard_it, limit=2)
        shard_it = out["NextShardIterator"]
        print out
        time.sleep(0.2)
        # {u'Records': [{u'PartitionKey': u'partitionkey', u'Data': u'{"lastname": "Rau", "age": 23, "firstname": "Peyton", "gender": "male"}', u'SequenceNumber': u'49547280908463336004254488250517179461390244620594577410'}, {u'PartitionKey': u'partitionkey', u'Data': u'{"lastname": "Mante", "age": 29, "firstname": "Betsy", "gender": "male"}', u'SequenceNumber': u'49547280908463336004254488250518388387209859249769283586'}], u'NextShardIterator': u'AAAAAAAAAAEvI7MPAuwLucWMwYtZnATetztUUTqgtQaTaihyV/+buCmSqBdKnAwv2dMNeGlYo3fvYCcH6aI/A+DtG3uq+MnG8AlyrX7UrHnlX5OF0xG/IEhSJyyToPvwtJ8odDoWShib3bjuk+944QcsPrRRsUsBNx6xyKgnY+xi9lXvweiImL1ByK5Bdj0sLoRp/9nBWfw='}


if __name__ == "__main__":
    print('############ CONNECTING TO AWS')
    _kinesis = kinesis.connect_to_region(KINESIS_REGION)
    print('############ CREATING NEW STREAM')
    stream = KinesisStream(_kinesis)
    print('############ NEW STREAM DESC')
    stream.describe()
    print('############ WATCHING STREAM')
    watch(_kinesis, stream)
    print('############ STARTING POPULATING')
    stream.start()
    print('############ NEW STREAM DESC')
    stream.describe()
    print('############ CLOSING STREAM')
    kinesis.delete_stream(KINESIS_STREAM_ID)
