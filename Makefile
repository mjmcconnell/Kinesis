app-run:
	docker-compose run --rm --service-ports app

app-bash:
	docker-compose run --rm --service-ports app bash
