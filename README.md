# QwikGeo API

![QwikGeo Image](/docs/docs/assests/images/qwikgeo.png)

QwikGeo API is a enterprise scale api for a GIS portal. QwikGeo API is written in [Python](https://www.python.org/) using the [FastAPI](https://fastapi.tiangolo.com/) web framework. 

---

**Source Code**: <a href="https://github.com/qwikgeo/qwikgeo-api" target="_blank">https://github.com/qwikgeo/qwikgeo-api</a>

---

## Tech Docs

Docs available at [this link](https://docs.qwikgeo.com).

## Requirements

QwikGeo API requires PostGIS >= 2.4.0.

## Configuration

In order for the api to work you will need to edit the .env with your database to host the API.

```
DB_HOST=localhost
DB_DATABASE=qwikgeo
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
CACHE_AGE_IN_SECONDS=0
MAX_FEATURES_PER_TILE=100000
SECRET_KEY=asdasasfakjh324fds876921vdas7tfv1uqw76fasd87g2q
GOOGLE_CLIENT_ID=asdasdas745-cj472811c26nu77fm5m98dasdasdasda1vkvk2pscfasad.apps.googleusercontent.com
JWT_TOKEN_EXPIRE_IN_MIUNTES=60000
```

## Usage

### Running Locally

To run the app locally `uvicorn main:app --reload`

### Production
Build Dockerfile into a docker image to deploy to the cloud.

## Aerich Commmands

`aerich init -t main.DB_CONFIG --location migrations -s .`

`aerich init-db`