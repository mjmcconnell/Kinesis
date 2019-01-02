# stdlib imports
import json

# third-party imports
from boto import kinesis

# local imports
from config import KINESIS_REGION
from config import KINESIS_STREAM_ID
from models import User


kinesis = kinesis.connect_to_region(KINESIS_REGION)
stream = kinesis.create_stream(KINESIS_STREAM_ID, 1)
kinesis.describe_stream(KINESIS_STREAM_ID)
# {u'StreamDescription': {u'HasMoreShards': False, u'StreamStatus': u'CREATING', u'StreamName': u'BotoDemo', u'StreamARN': u'arn:aws:kinesis:eu-west-1:374311255271:stream/BotoDemo', u'Shards': []}}
kinesis.list_streams()
# {u'StreamNames': [u'BotoDemo', u'IoTSensorDemo'], u'HasMoreStreams': False}


def fetch_users():
    for user in User().generate(50):
        kinesis.put_record("BotoDemo", json.dumps(user), "partitionkey")
