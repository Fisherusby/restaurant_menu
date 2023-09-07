# Restaurant menu

## I. About

This is project as a result of YLab`s intensive course

**For whom?**

This REST API for restaurants to publish and manage their food menu


**What can I do?**

Manage the dish`s menus.
- Your can create, read, edit and delete menus.
- Your can create, read, edit and delete submenus of menus.
- Your can create, read, edit and delete dishes of submenus.


## II. Used Tech Stack

- FastAPI
- Docker Compose
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- pytest
- Celery+RabbitMQ

## III. Quick run

Clone project
```commandline
git clone https://github.com/Fisherusby/restaurant_menu.git
```

Move into the project directory:
```commandline
cd restaurant_men
```

Rename .env to .env-dev
```commandline
mv .env-dev .env
```
Build and run docker compose
```commandline
docker compose up -d --build
```

## IV. Run tests

For running tests you need to execute script run_tests.sh
```
docker compose -f docker-compose-tests.yml up --build
```

## V. UI Api Documentation (Swagger endpoint)
http://localhost:8000/swagger

## VI. Stop docker-compose

```
docker compose down
```
or with clearing DB
```commandline
docker compose down -v
```
