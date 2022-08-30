# Authentication Endpoints

| Method | URL                                                                              | Description                           |
| ------ | -------------------------------------------------------------------------------- | --------------------------------------|
| `POST`  | `/api/v1/authentication/token`                                                  | [Token](#token)                       |
| `POST`  | `/api/v1/authentication/user`                                                   | [Create User](#create-user)           |
| `PUT`  | `/api/v1/authentication/user`                                                    | [Update User](#update-user)           |
| `GET`  | `/api/v1/authentication/user`                                                    | [View User](#view-user)               |

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