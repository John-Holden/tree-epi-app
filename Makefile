


# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


# Build the containers from scratch
build: ## Build the release and develoment container. Args: frontend | backend
	docker-compose build --no-cache ${SERVICE}

quick-build:
	docker-compose build ${SERVICE}

up-non-d: ## Run containers in non-detached mode
	docker-compose up ${SERVICE}

up: ## Run containers in detached mode by default
	docker-compose up -d ${SERVICE}

stop: ## Stop all docker containers
	docker-compose stop ${SERVICE}

rebuild-front: ## Rebuild react app, build new image & run frontend container in detached mode
	make stop SERVICE=frontend
	cd front/app/ && yarn build-docker-dev
	make quick-build SERVICE=frontend
	make up SERVICE=frontend

rebuild-back:
	make stop SERVICE=backend
	cd back/ && make compile_SIR
	make quick-build SERVICE=backend
	make up SERVICE=backend

follow-logs-back:
	docker logs --follow tree-epi-back

follow-logs-front:
	docker logs --follow tree-epi-front

exec:
	docker exec -it ${SERVICE} /bin/bash
