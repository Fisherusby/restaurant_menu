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
6. ** Реализовать в тестах аналог Django reverse() для FastAPI (✅ _**Сделано**_ [tests/utils/reverse.py](tests/utils/reverse.py))

Требования:
- Код должен проходить все линтеры. (_**PASS**_)
- Код должен соответствовать принципам SOLID, DRY, KISS. (_**PASS**_)
- Проект должен запускаться по одной команде (докер). (_**PASS**_)
- Проект должен проходить все Postman тесты (коллекция с Вебинара №1). (_**PASS**_)
- Тесты написанные вами после Вебинара №2, должны быть актуальны, запускать и успешно проходить (_**PASS**_)


### part 4

В этом домашнем задании необходимо:
1. Переписать текущее FastAPI приложение на асинхронное выполнение (✅ _**Сделано, со старта проета**_)
2. Добавить в проект фоновую задачу с помощью Celery + RabbitMQ. (✅ _**Сделано**_ [Celery](workers/celery.py) и [service](core/services/admin_xls.py))
3. Добавить эндпоинт (GET) для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами (✅ _**Сделано**_ добавлен ендпоинт [all_in_one](core/endpoints/all_in_one.py) и [тесты для него](tests/test_all_in_one.py)).
4. Реализовать инвалидация кэша в background task (встроено в FastAPI) (✅ _**Сделано**_ логика в сервисах для сущностей [service method request_google_sheet](core/services/admin_xls.py)
5. *Обновление меню из google sheets раз в 15 сек (✅ _**Сделано**_ [Добавлено расписание](workers/celery.py)  в качестве источника для обновления можно указывать как ссылку на файл так и ссылку на google sheets).
6. **Блюда по акции. Размер скидки (%) указывается в столбце G файла Menu.xlsx (✅ _**Сделано**_ При наличии скидок на блюдо ана учитываеться в GET запросах в которых есть блюда. [service method __apply_discount](core/services/admin_xls.py) Отоброжение [service method to_schema_with_discount](core/services/dishes.py))

Фоновая задача: синхронизация Excel документа и БД.
- В проекте создаем папку admin. В эту папку кладем файл Menu.xlsx (будет прикреплен к ДЗ). Не забываем запушить в гит (✅ _**Сделано**_ [Menu.xlsx](admin/Menu.xlsx)).
- При внесении изменений в файл все изменения должны отображаться в БД. Периодичность обновления 15 сек. Удалять БД при каждом обновлении – нельзя (✅ _**Сделано**_ [Celery](workers/celery.py) и [service](core/services/admin_xls.py))..


Требования:
* Данные меню, подменю, блюд для нового эндпоинта должны доставаться одним ORM-запросом в БД (использовать подзапросы и агрегирующие функций SQL). (_**PASS**_ [одним запросом](core/repositories/menus.py)))
* Проект должен запускаться одной командой (_**PASS**_)
* Проект должен соответствовать требованиям всех предыдущих вебинаров. (Не забыть добавить тесты для нового API эндпоинта) (_**PASS**_ [тесты для него](tests/test_all_in_one.py))


#### !!! PS. Обновление из файла !!!
Источник синхронизации указываем в .env как ADMIN_DATA_SOURCE и переодичность обновления в секундах ADMIN_DATA_UPDATE_PERIODIC.
В качестве источника синхронизация можно указать как xlsx файл так и google sheets (.env_dev уже содержит закоменченую строку с таблицей). Ранер сам разбереться что это.<br>
Общая логика в том что главный критерий для сущности это его UUID и зависимости от родительского UUID. То есть при изменении UUID сущности или UUID родителя считается что это новая сущность.
Сравнение идет по иерархии сущностей по их зависимостям и составляется список необходимых изменений. Который применяется в определенном порядке:
1. menu > DELETE > UPDATE > CREATE
2. submenu >  DELETE > UPDATE > CREATE
3. dish >  DELETE > UPDATE > CREATE

Если удаляется целое меню то удаление дочерних сущностей происходит по каскаду без лишних операций.
Обновление скидок вставлено как “отдельный процесс”. Что надо добавляется или изменяется или удаляется.

В логи celery пишеться вся информация о процессе синхронизации

#### PPS. Celery

Добавлена ручка для возможности ручного запуска таски на синхронизацию /api/v1/celery/task_sync_with
в качестве source передаем ссылку на файл или google sheets