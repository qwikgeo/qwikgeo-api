# Authentication Endpoints

| Method | URL                                                                              | Description                           |
| ------ | -------------------------------------------------------------------------------- | --------------------------------------|
| `POST`  | `https://api.qwikgeo.com/api/v1/authentication/token`                                                  | [Token](#token)                       |
| `POST`  | `https://api.qwikgeo.com/api/v1/authentication/google_token_authenticate`                              | [Google Token Authenticate](#google-token-authenticate)   |


## Endpoint Description's

## Token

### Description
The token endpoint allows you to receive a JWT token to authenticate with the API.

Token endpoint is available at `https://api.qwikgeo.com/api/v1/authentication/token`

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
    "token_type": "Bearer"
}
```

## Google Token Authenticate

### Description
The token endpoint allows you to receive a JWT token to authenticate with the API via a Google JWT Token.

Google Token Authenticate endpoint is available at `https://api.qwikgeo.com/api/v1/authentication/google_token_authenticate`

### Example Input 
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6M30.PJZEu9eDOBqSQTWJkNMCdV__tvuETyEVRwA5wH9Ansc"
}
```

### Example Output
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6M30.PJZEu9eDOBqSQTWJkNMCdV__tvuETyEVRwA5wH9Ansc",
    "token_type": "Bearer"
}
```
