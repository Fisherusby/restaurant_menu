# ylab

## I. Задание

Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции. Для проверки задания, к презентаций будет приложена Postman коллекция с тестами. Задание выполнено, если все тесты проходят успешно.
Даны 3 сущности: Меню, Подменю, Блюдо.

Зависимости:
- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

Условия:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.
- Во время запуска тестового сценария БД должна быть пуста.

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

