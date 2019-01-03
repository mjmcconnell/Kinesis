start:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.create()'

list:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.list()'

describe:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.describe('$(stream_name)')'

watch:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.watch('$(shard_id)')'

load:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.load()'

close:
	python -c 'from main import KinesisStreamManager; KinesisStreamManager.close()'
