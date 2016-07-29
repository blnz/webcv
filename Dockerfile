FROM node:latest

RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/src
RUN mkdir -p /usr/src/app/build
RUN mkdir -p /usr/src/app/config

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/app

COPY ./package.json /usr/src/app
COPY ./.babelrc /usr/src/app
COPY ./webpack-production.config.js /usr/src/app

COPY ./server.js /usr/src/app
COPY ./webpack-production.config.js /usr/src/app
COPY ./webpack-dev-server.config.js /usr/src/app
COPY ./config /usr/src/app/config
COPY ./src /usr/src/app/src

RUN npm install webpack -g
RUN npm install
RUN npm run build

EXPOSE 3000
EXPOSE 8888

CMD [ "node", "./server.js", "production" ]
