# KINESIS_REGION
#
# AWS region where the stream should be hosted from
KINESIS_REGION = 'eu-west-2'

# KINESIS_STREAM_ID
#
# Type: String
# Length Constraints: Minimum length of 1. Maximum length of 128.
# Pattern: [a-zA-Z0-9_.-]+
#
# A name to identify the stream. The stream name is scoped to the AWS account
# used by the application that creates the stream. It is also scoped by AWS
# Region. That is, two streams in two different AWS accounts can have the same
# name. Two streams in the same AWS account but in two different Regions can
# also have the same name.
KINESIS_STREAM_ID = 'marks-test-kinesis-stream'
