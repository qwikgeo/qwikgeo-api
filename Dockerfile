FROM ubuntu:14.04

RUN apt-get -qqy update && \
    apt-get install -qqy software-properties-common --no-install-recommends && \
    apt-add-repository -y ppa:ubuntugis/ppa && \
    apt-get install -qqy \
        wget \
        build-essential \
        gdal-bin \
        libgdal-dev \
        libspatialindex-dev \
        python \
        python-dev \
        python-pip 

WORKDIR /

RUN apt-add-repository ppa:ubuntugis/ubuntugis-unstable

RUN apt-get update

RUN apt-get -qqy install python-gdal

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]