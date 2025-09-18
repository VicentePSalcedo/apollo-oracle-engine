default: test

down:
    @docker-compose down

monitor:
    @docker compose logs -f app

run-now:
    @echo "Executing main.py now..."
    @docker exec python_app_container python /app/main.py

run script:
    @docker exec -it python_app_container python /app/{{script}}

reset:
    @docker-compose down -v

test: up run-now

up:
    @docker-compose up --build -d
