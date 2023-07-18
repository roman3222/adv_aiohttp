FROM python:3.11.3-alpine3.18


COPY ./app /app
WORKDIR /app

RUN pip install --no-cache-dir -r ./requirements.txt


ENTRYPOINT sh ./entrypoint.sh