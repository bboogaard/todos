init:
	docker-compose run web scripts/init.sh

migrations:
	docker-compose run web scripts/migrations.sh

migrate:
	docker-compose run web scripts/migrate.sh

index:
	docker-compose run web scripts/index.sh

test:
	docker-compose run web scripts/test.sh
