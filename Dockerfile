FROM python:3.12-slim

RUN apt-get update && apt-get install -y gcc
RUN pip install poetry uwsgi
RUN poetry config virtualenvs.create false

COPY . /flask
RUN chmod +x /flask/entrypoint.sh
WORKDIR /flask

RUN poetry install --only main

ENTRYPOINT ["./entrypoint.sh"]