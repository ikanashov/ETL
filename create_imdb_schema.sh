#!/bin/bash

# Забираем переменные настройки postgreSQL для поключения 
source .env
POSTGRES_URI="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

#Запускаем скрипт генерирующий схему базы данных
sudo docker-compose exec -T postgrescinema psql $POSTGRES_URI -A -q -t < db/schema_design/create_imdb_db_schema.sql
