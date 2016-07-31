FROM node:latest

RUN mkdir -p /usr/webcv
RUN mkdir -p /usr/webcv/src
RUN mkdir -p /usr/webcv/build
RUN mkdir -p /usr/webcv/config

RUN apt-get update && apt-get install -y \
    curl \
    git \
    zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/webcv

COPY ./package.json /usr/webcv
COPY ./.babelrc /usr/webcv
COPY ./webpack-production.config.js /usr/webcv

COPY ./server.js /usr/webcv
COPY ./webpack-production.config.js /usr/webcv
COPY ./webpack-dev-server.config.js /usr/webcv
COPY ./config /usr/webcv/config
COPY ./src /usr/webcv/src

RUN npm install webpack -g
RUN npm install
RUN npm run build

EXPOSE 3000

CMD [ "node", "./server.js", "production" ]
