# Инструкция по запуску монолитного Django-приложения с использованием Docker Compose

Этот репозиторий содержит монолитное Django-приложение, которое использует Docker Compose для контейнеризации. Следуя этой инструкции, вы сможете запустить приложение на своем компьютере.

## Предварительные требования

Убедитесь, что у вас установлены следующие компоненты:

- Docker (https://www.docker.com/products/docker-desktop)
- Docker Compose (обычно поставляется вместе с Docker)

## Запуск приложения

1. Склонируйте данный репозиторий на ваш компьютер и перейдите в папку проекта:

```
git clone https://github.com/JustGithubProject/DjangoBuShop.git project
cd project
docker-compose build
docker-compose up
```
