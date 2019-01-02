# third-party imports
from boto import kinesis

# local imports
from config import KINESIS_REGION
from config import KINESIS_STREAM_ID


kinesis = kinesis.connect_to_region(KINESIS_REGION)
stream = kinesis.create_stream(KINESIS_STREAM_ID, 1)
kinesis.describe_stream(KINESIS_STREAM_ID)
# {u'StreamDescription': {u'HasMoreShards': False, u'StreamStatus': u'CREATING', u'StreamName': u'BotoDemo', u'StreamARN': u'arn:aws:kinesis:eu-west-1:374311255271:stream/BotoDemo', u'Shards': []}}
kinesis.list_streams()
# {u'StreamNames': [u'BotoDemo', u'IoTSensorDemo'], u'HasMoreStreams': False}
