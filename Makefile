create:
	docker-compose build development

clean:
	docker system prune -f
	docker-compose stop
	docker rmi `docker images -a -q`

fresh:
	docker-compose build --no-cache development

run:
	docker-compose run --rm development
