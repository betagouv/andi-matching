FROM python:3.7-slim-buster

RUN pip install pipenv

ARG PG_DSN="postgress://user:pass@localhost:5432/db"
ARG HOST="localhost"
ARG PORT=9000
ENV PG_DSN=$PG_DSN
ENV HOST=$HOST
ENV PORT=$PORT

COPY Pipfile* /
RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y
RUN pipenv install --system --deploy

COPY matching/ /matching
COPY webservice/ /webservice
COPY Makefile /

WORKDIR /

ENTRYPOINT ["make", "serve"]
# ENTRYPOINT ["/bin/bash"]
