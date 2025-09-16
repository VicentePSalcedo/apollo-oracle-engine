default: test

commit:
    git status
    git add .
    gemini -p "Write a git commit for the staged changes and commit them."
    git push

down:
    docker-compose down

monitor:
    docker compose logs -f app

run script:
    @docker exec -it python_app_container python /app/{{script}}

reset:
    docker-compose down -v

test: up monitor

up:
    docker-compose up --build -d

