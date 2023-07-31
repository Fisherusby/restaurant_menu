#!/bin/sh
# check docker compose available version
if docker compose version; then
  docker_compose="docker compose"
elif docker-compose version; then
  docker_compose="docker-compose"
else
  echo "\033[1;31mDocker compose not found. Install it and try again\033[0m"
  exit 1
fi

# Up test docker containers
echo "\033[1;34m=== Up test environment ===\033[0m"
$docker_compose -f docker-compose-tests.yml up -d --build
echo "\033[1;34m=== Run tests in container ===\033[0m"
docker exec fastapi_backend_test python3 -m pytest -v
#docker exec fastapi_backend_test python3 -m pytest tests/test_menus.py::TestMenus::test_get_menu_detail -vv -s
#docker exec fastapi_backend_test python3 -m pytest tests/test_api_flow.py -vv -s
echo "\033[1;34m=== Down test environment ===\033[0m"
$docker_compose -f docker-compose-tests.yml down -v
