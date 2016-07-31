FROM buildpack-deps:jessie

RUN apt-get update && apt-get install -y \
    curl \
    git \
    python-pip \
    python2.7-dev \
    zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/webcv

COPY ./server.py /usr/webcv
COPY ./opencv.py /usr/webcv

COPY ./db /usr/webcv/db

RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y unzip wget build-essential \
		cmake git pkg-config libswscale-dev \
		python3-dev python3-numpy python3-pip \
		libtbb2 libtbb-dev libjpeg-dev \
		libpng-dev libtiff-dev libjasper-dev \
                libblas-dev liblapack-dev \
                sqlite3

RUN echo 'downloading and building opencv'
RUN cd \
	&& wget https://github.com/opencv/opencv/archive/3.1.0.zip \
	&& unzip 3.1.0.zip \
        && wget -O contrib.zip https://github.com/opencv/opencv_contrib/archive/master.zip \
        && unzip contrib.zip \ 
	&& cd opencv-3.1.0 \
	&& mkdir build \
	&& cd build \
	&& cmake -D OPENCV_EXTRA_MODULES_PATH=/root/opencv_contrib-master/modules .. \
	&& make -j3 \
	&& make install \
	&& cd \
	&& rm 3.1.0.zip contrib.zip

RUN pip3 install tornado Pillow Peewee

RUN mkdir -p /usr/webcv
RUN mkdir -p /usr/webcv/db

WORKDIR /usr/webcv

COPY ./server.py /usr/webcv
COPY ./opencv.py /usr/webcv

COPY ./db /usr/webcv/db

RUN echo 'initializing database with sample faces'
RUN mkdir data && cd data \
        && sqlite3 images.db < ../db/create_db.sql \
        && wget http://www.cl.cam.ac.uk/Research/DTG/attarchive/pub/data/att_faces.tar.Z \
        && tar zxvf att_faces.tar.Z \
        && mv orl_faces images \
        && cp /root/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_alt.xml .

EXPOSE 8888

CMD [ "python3", "./server.py" ]
