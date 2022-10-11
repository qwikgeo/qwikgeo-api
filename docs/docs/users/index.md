# Users Endpoints

| Method | URL                                                                              | Description                           |
| ------ | -------------------------------------------------------------------------------- | --------------------------------------|
| `POST`  | `https://api.qwikgeo.com/api/v1/users/user`                                     | [Create User](#create-user)           |
| `GET`  | `https://api.qwikgeo.com/api/v1/users/user`                                      | [User](#user)                         |
| `PUT`  | `https://api.qwikgeo.com/api/v1/users/user`                                      | [Update User](#update-user)           |
| `DELETE`  | `https://api.qwikgeo.com/api/v1/users/user`                                   | [Delete User](#delete-user)           |
| `GET`  | `https://api.qwikgeo.com/api/v1/users/search`                                    | [User Search](#user-search)           |

## Endpoint Description's

## Create User

### Description
The create user endpoint allows you to create a new user to use QwikGeo.

Create user endpoint is available at `https://api.qwikgeo.com/api/v1/users/user`

### Example Input 
```json
{
    "username": "johndoe",
    "password_hash": "secret",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@email.com"
}
```

### Example Output
```json
{
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@email.com",
    "photo_url": null,
    "created_at": "2022-08-19T18:44:55.415824+00:00",
    "modified_at": "2022-08-19T18:44:55.415846+00:00"
}
```

## User

### Description
The user endpoint allows you to view your user information.

User endpoint is available at `https://api.qwikgeo.com/api/v1/users/user`

### Example Output
```json
{
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@email.com",
    "photo_url": null,
    "created_at": "2022-08-19T18:44:55.415824+00:00",
    "modified_at": "2022-08-19T18:44:55.415846+00:00"
}
```

## Update User

### Description
The update user endpoint allows you to update information about your account.

Update user endpoint is available at `https://api.qwikgeo.com/api/v1/users/user`

### Example Input 
```json
{
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "newjohndoe@email.com"
}
```

### Example Output
```json
{
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "newjohndoe@email.com",
    "photo_url": null,
    "created_at": "2022-08-19T18:44:55.415824+00:00",
    "modified_at": "2022-08-19T18:44:55.415846+00:00"
}
```

## Delete User

### Description
The delete user endpoint allows you to delete your account.

Delete user endpoint is available at `https://api.qwikgeo.com/api/v1/users/user`

### Example Output
```json
{
    "message": "Deleted user."
}
```

## User Search

### Description
The update user endpoint allows you to update information about your account.

Update user endpoint is available at `https://api.qwikgeo.com/api/v1/users/user_search`

### Example

Search for users who username contain `john`.

### Example Input 
```shell
curl `https://api.qwikgeo.com/api/v1/users/user_search?username=john`
```

### Example Output
```json
{
    "users": [
        {
            "username": "johndoe",

        }
    ]
}
```