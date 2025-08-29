default: test

down:
    docker-compose down

monitor:
    docker compose logs -f app

reset:
    docker-compose down -v

test: reset up monitor

up:
    docker-compose up --build -d

