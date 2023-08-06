# ylab

## I. Задание

### part 1

Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции. Для проверки задания, к презентаций будет приложена Postman коллекция с тестами. Задание выполнено, если все тесты проходят успешно.
Даны 3 сущности: Меню, Подменю, Блюдо. (✅ _**Сделано**_)

Зависимости (✅ _**Сделано**_):
- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

Условия (✅ _**Сделано**_):
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
✅ _**Реализовано в первой части**_

Образы для Docker: <br>
(API) python:3.10-slim <br>
(DB) postgres:15.1-alpine <br>
(✅ _**Необходимые образы использованы**_)

1. Написать CRUD тесты для ранее разработанного API с помощью библиотеки pytest (✅ _**Сделано**_ [tests/](tests))
2. Подготовить отдельный контейнер для запуска тестов. Команду для запуска указать в README.md (✅ _**Сделано**_ [linc](https://github.com/Fisherus/ylab-dz1#iv-run-tests))
3. \* Реализовать вывод количества подменю и блюд для Меню через один (сложный) ORM запрос. (✅ _**Сделано**_ [Menu: core/repositories/menus.py](core/repositories/menus.py), [Submenu: core/repositories/submenus.py](core/repositories/submenus.py))
4. ** Реализовать тестовый сценарий «Проверка кол-ва блюд и подменю в меню» из Postman с помощью pytest (✅ _**Сделано**_ [Menu: tests/test_api_flow.py::TestApiFlow](tests/test_api_flow.py))

Если FastAPI синхронное - тесты синхронные, Если асинхронное - тесты асинхронные (✅ _**Сделано**_ тесты асинхронные)

*** _**Добавлен** [github action workflow](.github/workflows/tests.yml) для тестов (triggered automatically on push, pull request to main)_

### part 3

1. Вынести бизнес логику и запросы в БД в отдельные слои приложения (✅ _**Сделано, со старта проета**_).
2. Добавить кэширование запросов к API с использованием Redis. Не забыть про инвалидацию кэша. (✅ _**Сделано**_, логика в сервисах)
3. Добавить pre-commit хуки в проект. Файл yaml будет прикреплен к ДЗ. (✅ _**Сделано**_, дополнено poetry)
4. Покрыть проект type hints (тайпхинтами) (✅ _**Доработано**_ с учетом mypy)
5. *Описать ручки API в соответствий c OpenAPI (✅ _**Доработано**_. Добавлены контакты и общее описание, схема 404 где необходима, описаны все едпоинты)
6. ** Реализовать в тестах аналог Django reverse() для FastAPI (✅ _**Сделано**_)

Требования:
- Код должен проходить все линтеры. (_**PASS**_)
- Код должен соответствовать принципам SOLID, DRY, KISS. (_**PASS**_)
- Проект должен запускаться по одной команде (докер). (_**PASS**_)
- Проект должен проходить все Postman тесты (коллекция с Вебинара №1). (_**PASS**_)
- Тесты написанные вами после Вебинара №2, должны быть актуальны, запускать и успешно проходить (_**PASS**_)

## TODO:
- Rework cache logic to decorators
- Add tests\assert for cache (redis mocking now )
- Rework tests with a snapshot
- Make more readable parametrize in tests

## II. Used Tech Stack

- FastAPI
- Docker Compose
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- pytest

## III. Quick run

Clone project
```commandline
git clone https://github.com/Fisherus/ylab-dz1
```

Move into the project directory:
```commandline
cd ylab-dz1
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
