init:
	docker-compose run web scripts/init.sh

migrations:
	docker-compose run web scripts/migrations.sh

migrate:
	docker-compose run web scripts/migrate.sh

index:
	docker-compose run web scripts/index.sh

rebuild_index:
	docker-compose run web scripts/rebuild_index.sh

test:
	docker-compose run web scripts/test.sh

make_fixtures:
	docker-compose run web scripts/make_fixtures.sh
