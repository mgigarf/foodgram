[![Main Foodgram workflow](https://github.com/mgigarf/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/mgigarf/foodgram/actions/workflows/main.yml)

# Описание проекта

Сервис foodgram для публикации рецептов. Позволяет пользователям делиться рецептами, добавлять их себе в избранное и список покупок, а так же подготовиться к походу в магазин, скачав список ингридиентов для выбранных рецептов.

# Пример сайта
https://foodgramgigarf.ddns.net

# Стек
В проекте использованы следующие библиотеки:

    Python 3.9
    Django 3.2.16
    Django Rest Framework 3.12.4
    Posgresql
    Doker compose

# Запуск проекта
Скачать файл docker-compose.yml из репозитория 
``` bash
https://github.com/mgigarf/foodgram/blob/main/docker-compose.yml
```
Создать файл с переменными окружения .env в корне пректа
Список требуемых переменных:

    POSTGRES_DB=имя базы
    POSTGRES_USER=владелец базы
    POSTGRES_PASSWORD=пароль
    DB_NAME=имя базы
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=ключ приложения
    DEBUG=true/false
    ALLOWED_HOSTS=разрешенные хосты

Запустить Docker compose 
``` bash
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
```

Собрать статику и применить миграции
``` bash
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
```

Автор проекта 
[Селиванов Михаил](https://github.com/mgigarf)