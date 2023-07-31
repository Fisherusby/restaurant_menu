# ylab

## I. Задание

### part 1

Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции. Для проверки задания, к презентаций будет приложена Postman коллекция с тестами. Задание выполнено, если все тесты проходят успешно.
Даны 3 сущности: Меню, Подменю, Блюдо.

Зависимости:
- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

✅ Условия:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.
- Во время запуска тестового сценария БД должна быть пуста.

### part 2

Обернуть программные компоненты в контейнеры. Контейнеры должны запускаться по одной команде “docker-compose up -d” или той которая описана вами в readme.md. <br>
✅ Реализовано в первой части

Образы для Docker: <br> 
(API) python:3.10-slim <br>
(DB) postgres:15.1-alpine <br>
(✅ Необходимые образы использованы)

1. Написать CRUD тесты для ранее разработанного API с помощью библиотеки pytest (✅ [tests/](tests/))
2. Подготовить отдельный контейнер для запуска тестов. Команду для запуска указать в README.md (✅ [linc](https://github.com/Fisherus/ylab-dz1#iv-run-tests))
3. \* Реализовать вывод количества подменю и блюд для Меню через один (сложный) ORM запрос. (✅ [Menu: core/repositories/menus.py](core/repositories/menus.py), [Submenu: core/repositories/submenus.py](core/repositories/submenus.py))
4. ** Реализовать тестовый сценарий «Проверка кол-ва блюд и подменю в меню» из Postman с помощью pytest (✅ [Menu: tests/test_api_flow.py::TestApiFlow](tests/test_api_flow.py))

Если FastAPI синхронное - тесты синхронные, Если асинхронное - тесты асинхронные (✅ тесты асинхронные)

*** Добавлен [githab action workflow(.github/workflows/tests.yml)] для тестов (triggered automatically on push, pull request to main)

## II. Used Tech Stack

- FastAPI
- Docker Compose
- PostgreSQL
- SQLAlchemy
- Alembic

## III. Quick run

Clone project
```commandline
git clone https://github.com/Fisherus/ylab-dz1
```

Move into the project directory:
```commandline
cd ylab-dz1
```

Rename .env в .env-dev
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
/bin/sh ./run_tests.sh
```
or without using script:
- up test environment
```commandline
docker compose -f docker-compose-tests.yml up -d --build
```
- run tests
```
docker exec fastapi_backend_test python3 -m pytest -v
```
- down test environment after complicated
```
docker compose -f docker-compose-tests.yml down -v
```


## IV. UI Api Documentation (Swagger endpoint)
http://localhost:8000/swagger

## V. Stop docker-compose

```
docker compose down
```
or with clearing DB 
```commandline
docker compose down -v
```

