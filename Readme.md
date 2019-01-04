# Kinesis sample app

This app is setup to as a playground for learning AWS's Kinesis service.

Follows guidence from the official tutorial [here](https://aws.amazon.com/blogs/big-data/snakes-in-the-stream-feeding-and-eating-amazon-kinesis-streams-with-python/)

## Flow

1/ User enters number of records to generate from the web app
2/ App creates records and pushes them up to the Kinesis data stream
3/ The stream listener (Kinesis Firehose delivery streams), then captures the data in the stream, and places it into a buffer.
4/ Once the data within the buffer is full (default 5 MB) or expires (default 300 seconds), it is then written to a source (s3 bucket)

## Kinese limits

Amazon Kinesis Data Streams has the following stream and shard limits.

There is no upper limit on the number of shards you can have in a stream or account. It is common for a workload to have thousands of shards in a single stream.

There is no upper limit on the number of streams you can have in an account.

A single shard can ingest up to 1 MiB of data per second (including partition keys) or 1,000 records per second for writes. Similarly, if you scale your stream to 5,000 shards, the stream can ingest up to 5 GiB per second or 5 million records per second. If you need more ingest capacity, you can easily scale up the number of shards in the stream using the AWS Management Console or the `UpdateShardCount` API.

The default shard limit is 500 shards for the following AWS Regions: US East (N. Virginia), US West (Oregon), and EU (Ireland). For all other Regions, the default shard limit is 200 shards.

The maximum size of the data payload of a record before base64-encoding is up to 1 MiB.

`GetRecords` can retrieve up to 10 MiB of data per call from a single shard, and up to 10,000 records per call. Each call to `GetRecords` is counted as one read transaction.

Each shard can support up to five read transactions per second. Each read transaction can provide up to 10,000 records with an upper limit of 10 MiB per transaction.

Each shard can support up to a maximum total data read rate of 2 MiB per second via `GetRecords`. If a call to `GetRecords` returns 10 MiB, subsequent calls made within the next 5 seconds throw an exception.
