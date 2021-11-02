init:
	docker-compose run web scripts/init.sh

test:
	docker-compose run web scripts/test.sh
