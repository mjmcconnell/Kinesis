help:
	@echo "Kinesis"
	@echo ""
	@echo "The following commands are available:"
	@echo ""
	@echo "    make run:     Run local development server inside container."
	@echo "    make bash:    Opens an interactive terminal for a new instance."
	@echo "    make attach:  Opens an interactive terminal for the running instance."

run:
	docker-compose up

bash:
	docker-compose run --rm --service-ports app bash

attach:
	docker exec -it kinesis_app_1 bash
