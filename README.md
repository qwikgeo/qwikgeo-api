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

In order for the api to work you will need to edit the `config.py` file with your database connections.
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

## API

| Method | URL                                                                              | Description                                             |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `POST`  | `/api/v1/authentication/token`                                                  | [Token](#token)               |
| `POST`  | `/api/v1/authentication/user`                                                   | [Create User](#create-user)               |
| `PUT`  | `/api/v1/authentication/user`                                                    | [Update User](#update-user)               |
| `GET`  | `/api/v1/authentication/user`                                                    | [View User](#view-user)               |
| `GET`  | `/api/v1/health_check`                                                           | Server health check: returns `200 OK`   |

## Endpoint Description's

## Token

### Description
The token endpoint allows you to recieve a JWT token to authenticate with the API.


### Example Input 
```json
{
    "username": "mrider3",
    "password": "secret"
}
```

### Example Output
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6M30.PJZEu9eDOBqSQTWJkNMCdV__tvuETyEVRwA5wH9Ansc",
    "token_type": "bearer"
}
```

## Create User

### Description
The create user endpoint allows you to create a new user to use the application.

### Example Input 
```json
{
    "username": "mrider3",
    "password_hash": "secret"
}
```

### Example Output
```json
{
    "id": 1,
    "username": "mrider3",
    "password_hash": "$2b$12$/mV9SXGaslPAgjM7CBnDLuFLiwwKfy7Liz715lXewHlod0KKlp.Wu",
    "name": null,
    "created_at": "2022-08-19T18:44:55.415824+00:00",
    "modified_at": "2022-08-19T18:44:55.415846+00:00"
}
```

## Update User

### Description
The update user endpoint allows you to update information about your account.

### Example Input 
```json
{
    "username": "mrider3",
    "password_hash": "secret",
    "name": "Michael"
}
```

### Example Output
```json
{
    "id": 1,
    "username": "mrider3",
    "password_hash": "secret",
    "name": "Michael",
    "created_at": "2022-08-19T18:20:13.662074+00:00",
    "modified_at": "2022-08-19T18:20:13.662074+00:00"
}
```

## Delete User

### Description
The delete user endpoint allows you to delete your account.

### Example Output
```json
{
    "message": "Deleted user 1"
}
```