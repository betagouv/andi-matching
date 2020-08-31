FROM python:3.7-slim-buster

ARG AN4_PG_DSN="postgress://user:pass@localhost:5432/db"
ARG HOST="localhost"
ARG PORT=9000
ENV AN4_PG_DSN=$AN4_PG_DSN
ENV HOST=$HOST
ENV PORT=$PORT

RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y

COPY . /app
WORKDIR /app
RUN pip install .

ENTRYPOINT ["andi-api"]
