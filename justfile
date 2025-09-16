default: test

down:
    docker-compose down

monitor:
    docker compose logs -f app

run-now:
    @echo "Executing main.py now..."
    @docker exec python_app_container python /app/main.py

run script:
    @docker exec -it python_app_container python /app/{{script}}

reset:
    docker-compose down -v

test: reset up run-now monitor

up:
    docker-compose up --build -d