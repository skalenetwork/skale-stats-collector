FROM python:3.8-buster

RUN apt-get update
RUN apt-get install libpq-dev -y
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

COPY ./requirements.txt /skale-stats-collector/requirements.txt
WORKDIR /skale-stats-collector

RUN pip3 install -r requirements.txt
COPY . /skale-stats-collector
ENV PYTHONPATH="/skale-stats-collector"