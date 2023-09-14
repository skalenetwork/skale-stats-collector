FROM python:3.10-buster

RUN apt-get update
COPY ./requirements.txt /skale-stats-collector/requirements.txt
WORKDIR /skale-stats-collector

RUN pip3 install -r requirements.txt
COPY . /skale-stats-collector
ENV PYTHONPATH="/skale-stats-collector"