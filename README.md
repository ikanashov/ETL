# E-cinema
## [Выполнение заданий третьего спринта (ETL Postgres to Elastic)](postgres_to_es/README.md)

## Порядок запуска системы
Для работы системы необходимо наличие docker и docker-compose

Для запуска проекта необходимо создать в корневой папке проекта файл .env следующего содержимого:
```shell
POSTGRES_DB=cinema
POSTGRES_USER=yandex
POSTGRES_PASSWORD=<>
POSTGRES_HOST=localhost
POSTGRES_PORT=7654
POSTGRES_SCHEMA=public,imdb
DJANGO_HOST=dev.usurt.ru
DJANGO_PORT=8354
DJANGO_SECRET=<>
NGINX_HTTP_PORT=8080
REDIS_PASSWORD=<>
REDIS_PORT=9376
ELASTIC_PASSWORD=<>
ELASTIC_HOST=localhost
ELASTIC_PORT=9200
ELASTIC_SCHEME=http
ELASTIC_INDEX=movies
ELASTIC_USER=elastic
REDIS_PASSWORD=<>
REDIS_PORT=9376
REDIS_PREFIX=cinema
ETL_SIZE_LIMIT=7
```

POSTGRES_DB - имя базы данных  
POSTGRES_USER - имя пользователя базы данных  
POSTGRES_PASSWORD - пароль пользователя (можно сгенерировать с помощью команды ```openssl rand -hex 32```)  
POSTGRES_HOST - имя хоста базы данных  
POSTGRES_PORT - порт который будет проброшен наружу из контейнера postgres  
POSTGRES_SCHEMA - для корректной работы надо оставить значения public, imdb  
DJANGO_HOST - внешнее имя хоста с которого будет доступна админка django  
DJANGO_PORT - порт по которому будет доступен django внутри сети docker-compose  
NGINX_HTTP_PORT - внешний порт для веб-сервера nginx  
DJANGO_SECRET - секрет для Django (можно сгенерировать с помощью команды ```openssl rand -hex 32```)  
REDIS_PORT - порт который слушает REDIS внутри сети docker-compose
REDIS_PASSWORD - пароль для пользователя default (AUTH) (можно сгенерировать с помощью команды ```openssl rand -hex 32```)  
ELASTIC_PASSWORD - пароль elasticsearch (можно сгенерировать с помощью команды ```openssl rand -hex 32```)  
ELASTIC_HOST - имя хоста Elastic  
ELASTIC_PORT - порт Elastic  
ELASTIC_SCHEME - схема Elastic (http)  
ELASTIC_INDEX - индекс Elastic  
ELASTIC_USER - пользователь elastic  
ETL_SIZE_LIMIT - размер пачки данных которую обрабатывает ETL процесс за один раз  
  
Чтобы не создавать базу данных ее можно восстановить с помощью скрипта cinemaDB_restore.sh

После создания конфигурационного файла необходимо выполнить следующие команды в корневой папке проекта.
```shell
# запускаем все необходимы сервисы
./start
# скачиваем файлы с сайта imdb для импорта данных в сответствии со схемой (объем порядка 1 ГБ)
sudo docker-compose run -w /etl/db etlcinema /etl/db/get_imdb_data.sh
# создаем схему для данных из imdb и загружаем в нее данные
./create_imdb_schema.sh
sudo docker-compose run etlcinema python /etl/load_imdb.py

# инициализируем джанго приложение
sudo docker-compose exec djangocinema /cinema_admin/manage.py migrate
sudo docker-compose exec djangocinema /cinema_admin/manage.py createsuperuser
sudo docker-compose exec djangocinema /cinema_admin/manage.py collectstatic

# загружаем данные из базы sqlite в базу postgres созданную джанго
sudo docker-compose run etlcinema python /etl/dj_load_data.py
```

После выполения этих команд система буде доступна по протколу http и порту указанному в NGINX_HTTP_PORT  
  
Для остановки системы необходимо выполнить команду ```./stop```

## Задание второго спринта
### 1. Django API
Джанго находится в папке cinema_admin. Приложение в папке cinema.  
Настроены файлы urls.py  
Разработанное API находится в файле cinema/api/v1/views.py
Количество фильмов выдваемых по умолчанию задано в файле cinema/apps.py  
Схема API находися в папке openapi.  
Правильные тесты постман в папке tests.  

### 2. Docker
Файл конфигурации в корне проекта .env (необходимо создать по инструкции ниже).  
Основной файл c описанием сервисов docker-compose.yml.  
Созданы 4 сервиса postgrescinema (база данных postgres), djangocinema (приложение админики и api, запускается через uwsgi), nginxcinema (web сервер nginx), etlcinema (скрипты для инициализации базы данных, и загрузки данных из sqlite).  
Написаны Dockerfile для сервисов django (cinema_admin/Dockerfile), nginx (nginx/Dockerfile), etl (etl/Dockerfile).  
В сети для сервисов изменена IP адресация, чтобы избежать конфликтов с рабочим окружением.  

### 3. Nginx
Конфигурация nginx описана в двух файлах nginx.conf (базовые настройки) и cinema.config.template (настройки сервиса по заданию).  

