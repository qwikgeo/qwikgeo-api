FROM python:3.9

WORKDIR /

RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update && apt-get install -y gdal-bin python-gdal python3-gdal

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]