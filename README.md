# Тестовое задание

```shell
flask --app app.main db init
flask --app app.main db migrate -m "Initial migration."
flask --app app.main db upgrade
```

## Deployment

Создать файл `.env` с переменными окружения (примере `.env.example`).:
```shell
cp .env.example .env
```

Запустить контейнеры:
```shell
docker-compose --env-file .env up -d --build
```