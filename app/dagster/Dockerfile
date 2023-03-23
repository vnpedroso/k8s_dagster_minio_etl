# Python base image
FROM python:3.10.7-slim-bullseye

#Dagster version
ARG DAGSTER_VERSION=1.1.14

# System setup
RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends \
    default-jdk

#Other python requirements
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

#Dagster Install
RUN \
    pip install \
        dagster==${DAGSTER_VERSION} \
        dagster-postgres \
        dagster-celery[flower,redis,kubernetes] \
        dagster-aws \
        dagster-k8s \
        dagster-celery-k8s \
#Cleanup
    &&  rm -rf /var \
    &&  rm -rf /root/.cache  \
    &&  rm -rf /usr/lib/python2.7 \
    &&  rm -rf /usr/lib/x86_64-linux-gnu/guile \
    &&  rm /requirements.txt

#Our dagster code
COPY orpheus_project/ /