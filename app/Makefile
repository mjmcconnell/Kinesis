pip-install:
	pip install -r requirements.txt

run: pip-install
	flask run -h 0.0.0.0 -p 8080

create:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.create()'

enable_encryption:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.create()'

disable_encryption:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.create()'

status:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.status()'

list:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.list()'

describe:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.describe("$(stream_name)")'

watch:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.watch("$(shard_id)")'

load:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.load()'

close:
	@python -c 'from kinesis_manager import KinesisStreamManager; KinesisStreamManager.close()'
