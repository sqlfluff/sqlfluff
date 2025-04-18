.PHONY: help build clean fresh shell start stop

.DEFAULT_GOAL := help

help: ## Show this available targets
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the development container
	docker-compose build development

clean: ## Clean up all containers and images
	docker system prune -f
	docker-compose stop
	docker rmi `docker images -a -q`

fresh: ## Build the development container from scratch
	docker-compose build --no-cache development

shell: ## Start a bash session in the development container
	docker-compose exec development bash

start: ## Start the development container
	docker-compose up -d

stop: ## Stop the development container
	docker-compose stop
