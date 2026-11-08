# Tech Idea Hub

Веб-приложение для совместной работы над стартап-идеями. Включает канбан-доску, чат, систему приглашений и интерактивную доску для рисования.

## Стек технологий

*   **Бэкенд:** Python 3.11, Django 5, Django Channels, Daphne
*   **База данных:** PostgreSQL 15, Redis (для WebSocket)
*   **Фронтенд:** HTML, CSS, Vanilla JS, React (для доски)
*   **Инфраструктура:** Docker, Docker Compose, Nginx (для продакшена)

## Как запустить (через Docker)

Убедитесь, что у вас установлен [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/Anytkaa/TechIdea.git
    cd TechIdea

2.  Запустите сборку и старт контейнеров:
    docker compose up --build -d

3.  Откройте приложение в браузере:
    Сайт: http://localhost:8000