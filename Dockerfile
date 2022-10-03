FROM andrejreznik/python-gdal:py3.8.2-gdal3.0.4

WORKDIR /

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]