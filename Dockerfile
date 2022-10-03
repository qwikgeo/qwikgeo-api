FROM python:3.9

WORKDIR /

RUN apt-add-repository ppa:ubuntugis/ubuntugis-unstable

RUN apt-get update

RUN apt-get -qqy install python-gdal

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]