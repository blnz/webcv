FROM ubuntu:xenial

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git libmysqlclient-dev imagemagick libmagickwand-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python2.7 python2.7-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-pip libgd-dev libpuzzle-dev

RUN pip install MySQL-python
RUN pip install boto
RUN pip install requests
RUN pip install Wand facebook-sdk pypuzzle
RUN apt-get autoremove -y
RUN apt-get clean all

RUN mkdir -p /usr/src/app
COPY ./src /usr/src/app/
COPY ./bin /usr/bin

WORKDIR /usr/src/app

CMD ["./feedProcessor.py"]
