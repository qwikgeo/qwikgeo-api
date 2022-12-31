# Groups Endpoints

| Method | URL | Description |
| ------ | --- | ----------- |
| `GET` | `/api/v1/groups/` | [Groups](#groups)  |
| `POST` | `/api/v1/groups/` | [Create Group](#create-group)  |
| `GET` | `/api/v1/groups/{group_id}` | [Group](#group)  |
| `PUT` | `/api/v1/groups/{group_id}` | [Update Group](#update-group)  |
| `DELETE` | `/api/v1/groups/{group_id}` | [Delete Group](#delete-group)  |


## Endpoint Description's

## Groups

### Description
The groups endpoint returns all groups within QwikGeo.

Groups endpoint is available at `https://api.qwikgeo.com/api/v1/groups`

### Example Output
```json
[
    {
        "group_id": "f3ba05eb-dcce-4112-911f-147bb17ba866",
        "name": "New Group",
        "group_admins": [
            {
                "id": 1,
                "username": "mkeller3"
            }
        ],
        "group_users": [
            {
                "id": 7,
                "username": "mkeller3"
            }
        ]
    }
]
```

## Create Group

### Description
The create group endpoint allows you create a group within QwikGeo.

Tables endpoint is available at `https://api.qwikgeo.com/api/v1/groups/`

### Example Input
```json
{
    "name": "New Group 2",
    "group_admins": [
        {
            "id": 1,
            "username": "mkeller3"
        }
    ],
    "group_users": [
        {
            "id": 7,
            "username": "mkeller3"
        }
    ]
}
```

### Example Output
```json
{
    "group_id": "f3ba05eb-dcce-4112-911f-147bb17ba866",
    "name": "New Group 2",
    "group_admins": [
        {
            "id": 1,
            "username": "mkeller3"
        }
    ],
    "group_users": [
        {
            "id": 7,
            "username": "mkeller3"
        }
    ]
}
```

## Group

### Description
The group endpoint returns a group you have access to within QwikGeo.

Tables endpoint is available at `https://api.qwikgeo.com/api/v1/groups/{group_id}`

### Example Output
```json
{
    "group_id": "f3ba05eb-dcce-4112-911f-147bb17ba866",
    "name": "New Group",
    "group_admins": [
        {
            "id": 1,
            "username": "mkeller3"
        }
    ],
    "group_users": [
        {
            "id": 7,
            "username": "mkeller3"
        }
    ]
}
```

## Update Group

### Description
The update group endpoint allows you edit a group have admin access to within QwikGeo.

Tables endpoint is available at `https://api.qwikgeo.com/api/v1/groups/{group_id}`

### Example Input
```json
{
    "group_id": "f3ba05eb-dcce-4112-911f-147bb17ba866",
    "name": "New Group 2",
    "group_admins": [
        {
            "id": 1,
            "username": "mkeller3"
        }
    ],
    "group_users": [
        {
            "id": 7,
            "username": "mkeller3"
        }
    ]
}
```

### Example Output
```json
{
    "group_id": "f3ba05eb-dcce-4112-911f-147bb17ba866",
    "name": "New Group 2",
    "group_admins": [
        {
            "id": 1,
            "username": "mkeller3"
        }
    ],
    "group_users": [
        {
            "id": 7,
            "username": "mkeller3"
        }
    ]
}
```

## Delete Group

### Description
The delete group endpoint allows you edit a group have admin access to within QwikGeo.

Tables endpoint is available at `https://api.qwikgeo.com/api/v1/groups/{group_id}`

### Example Output
```json
{
    "status": true
}
```