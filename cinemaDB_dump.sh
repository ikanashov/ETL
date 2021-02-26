#!/bin/bash

# Забираем переменные настройки postgreSQL для поключения 
source .env
POSTGRES_URI="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

#Делаем полный дамп базы данных
sudo docker-compose exec postgrescinema pg_dump $POSTGRES_URI -n public -n content> db/cinemaDB.dump
