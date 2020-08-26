FROM ubuntu:20.04

MAINTAINER Amanjeev Sethi "aj@amanjeev.com"

RUN apt update -y
RUN apt upgrade -y
RUN apt install -y python3-pip python3-dev git

RUN mkdir -p /app
WORKDIR /app
COPY . .
RUN ls -lsa .

RUN python3 setup.py install

EXPOSE 5000
ENTRYPOINT [ "gunicorn", "--bind", ":5000", "--chdir", "bin", "run:app" ]