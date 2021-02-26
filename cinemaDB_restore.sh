#!/bin/bash

# Забираем переменные настройки postgreSQL для поключения 
source .env
POSTGRES_URI="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

#Восстанавливаем базу данных 
sudo docker-compose exec -T postgrescinema pg_restore $POSTGRES_URI < db/cinemaDB.dump
