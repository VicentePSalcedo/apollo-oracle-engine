default: test

down:
    docker-compose down

monitor:
    docker compose logs -f app

run script:
    @docker exec -d python_app_container python /app/{{script}}
    @just monitor

reset:
    docker-compose down -v

test: up monitor

up:
    docker-compose up --build -d

