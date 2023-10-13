#!/bin/bash

# Check if volumes already exist, if not create them
if [ "$(docker volume ls | grep users-data)" == "" ]; then
    docker volume create users-data
fi
if [ "$(docker volume ls | grep questions-data)" == "" ]; then
    docker volume create questions-data
fi
if [ "$(docker volume ls | grep rabbitmq-data)" == "" ]; then
    docker volume create rabbitmq-data
fi

# Bring down the services and remove all images, before building/starting.
docker-compose down --rmi all && docker-compose --env-file .env up --build "$@"
