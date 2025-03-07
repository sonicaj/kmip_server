COMPOSE_OPTIONS=-f docker-compose.yaml
CONTAINER=kmip.server

start:
	docker compose $(COMPOSE_OPTIONS) up -d

stop:
	docker compose $(COMPOSE_OPTIONS) stop

ssh:
	docker exec -it $(CONTAINER) /bin/bash
