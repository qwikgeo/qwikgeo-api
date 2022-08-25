# FastGeoPortal

FastGeoPortal is a enterprise scale api for a GIS portal. FastGeoPortal is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/mkeller3/FastGeoPortal" target="_blank">https://github.com/mkeller3/FastGeoPortal</a>

---

## Requirements

FastGeoPortal requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the .env with your database to host the GeoPortal.

```
DB_HOST=localhost
DB_DATABASE=geoportal
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
CACHE_AGE_IN_SECONDS=0
MAX_FEATURES_PER_TILE=100000
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.

## Aerich Commmands

`aerich init -t main.DB_CONFIG --location migrations -s .`

`aerich init-db`