# Items Endpoints

| Method | URL                                                                              | Description                                 |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------- |
| `GET`  | `https://api.qwikgeo.com/api/v1/items`                                                                  | [Items](#items)                   |
| `GET`  | `https://api.qwikgeo.com/api/v1/item/{portal_id}`                                                       | [Item](#item)                   |


## Endpoint Description's

## Items

### Description
The items endpoint returns a list of item you have access to within QwikGeo.

Items endpoint is available at `https://api.qwikgeo.com/api/v1/items`

```shell
curl https://api.qwikgeo.com/api/v1/items
```

### Example Output
```json
[
    {
        "portal_id": "4c2b7906-ca54-4343-b68b-13fe1a9175af",
        "title": "Tennessee State Parks",
        "created_time": "2022-10-07T14:04:56.224550+00:00",
        "modified_time": "2022-10-07T14:04:56.224643+00:00",
        "tags": [],
        "description": "",
        "views": 3,
        "searchable": true,
        "item_type": "table",
        "url": null,
        "item_read_access_list": [
            {
                "id": 1,
                "name": "mkeller3"
            }
        ],
        "item_write_access_list": [
            {
                "id": 1,
                "name": "mkeller3"
            }
        ],
        "table": [
            {
                "id": 1,
                "table_id": "vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps",
                "created_time": "2022-10-07T14:04:56.263222+00:00",
                "modified_time": "2022-10-07T14:04:56.263248+00:00"
            }
        ]
    }
]
```

## Item

### Description
The item endpoint returns an item you have access to within QwikGeo.

Items endpoint is available at `https://api.qwikgeo.com/api/v1/items/{portal_id}`

```shell
curl https://api.qwikgeo.com/api/v1/items/{portal_id}
```

### Example Output
```json
{
    "portal_id": "4c2b7906-ca54-4343-b68b-13fe1a9175af",
    "title": "Tennessee State Parks",
    "created_time": "2022-10-07T14:04:56.224550+00:00",
    "modified_time": "2022-10-07T14:04:56.224643+00:00",
    "tags": [],
    "description": "",
    "views": 3,
    "searchable": true,
    "item_type": "table",
    "url": null,
    "item_read_access_list": [
        {
            "id": 1,
            "name": "mkeller3"
        }
    ],
    "item_write_access_list": [
        {
            "id": 1,
            "name": "mkeller3"
        }
    ],
    "table": [
        {
            "id": 1,
            "table_id": "vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps",
            "created_time": "2022-10-07T14:04:56.263222+00:00",
            "modified_time": "2022-10-07T14:04:56.263248+00:00"
        }
    ]
}
```