FROM python:3.9

WORKDIR /app
ENV PYTHONPATH=/app;/app/src
RUN apt-get -y update
RUN apt-get -y install git

COPY requirements.txt /requirements.txt
COPY requirements_dev.txt /requirements_dev.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt --upgrade --default-timeout=100
RUN pip install -r /requirements_dev.txt --upgrade --default-timeout=100
