# pull official base image
FROM python:3.8.0-slim

# set work directory
WORKDIR /usr/local/site/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PG_VERSION=11

# install psycopg2 dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install  -y\
       gcc \
       g++ \
       postgresql-server-dev-$PG_VERSION \
       musl-dev \
    && apt-get install -y \
       gettext \
       postgresql-client-$PG_VERSION \
    && apt-get install  -y\
       binutils libproj-dev libgeos++ proj-bin libgdal20 python3-gdal

# install dependencies
RUN set -ex && \
    pip install --upgrade pip
COPY ./requirements.txt /usr/local/site/requirements.txt
RUN set -ex && \
    pip install -r requirements.txt

# copy project
COPY . /usr/local/site/