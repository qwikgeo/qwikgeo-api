# FastGeoPortal

FastGeoPortal is a enterprise scale GIS portal. FastGeoPortal is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/mkeller3/FastGeoPortal" target="_blank">https://github.com/mkeller3/FastGeoPortal</a>

---

## Requirements

FastGeoPortal requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the  DB_CONFIG variable in `main.py` file with your database connections.

Example
```python
DB_CONFIG = {
    "connections": {
        "default": "postgres://postgres:postgres@localhost:5432/geoportal"
    },
    "apps": {
        "models": {
            "models": ["db_models", "aerich.models"],
            "default_connection": "default",
        },
    }
}
```

You will also need to edit the `config.py` file with your database connections.
```python
DATABASES = {
    "data": {
        "host": "localhost", # Hostname of the server
        "database": "data", # Name of the database
        "username": "postgres", # Name of the user, ideally only SELECT rights
        "password": "postgres", # Password of the user
        "port": 5432, # Port number for PostgreSQL
    }
}
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.