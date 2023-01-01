# Tables Endpoints

| Method | URL                                                                              | Description                                 |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------- |
| `GET`  | `https://api.qwikgeo.com/api/v1/tables`                                                           | [Tables](#table)                   |
| `GET`  | `https://api.qwikgeo.com/api/v1/tables/{table_id}`                                                | [Table](#table)                   |
| `POST`  | `https://api.qwikgeo.com/api/v1/tables/`                                             | [Create Table](#create-table)               |
| `DELETE`  | `https://api.qwikgeo.com/api/v1/tables/{table_id}`                                             | [Delete Table](#delete-table)               |
| `POST`  | `https://api.qwikgeo.com/api/v1/tables/{table_id}/add_column`                                    | [Add Column](#add-column)                   |
| `DELETE`  | `https://api.qwikgeo.com/api/v1/tables/{table_id}/delete_column`                               | [Delete Column](#delete-column)             |


## Endpoint Description's

## Tables

### Description
The tables endpoint returns tables you have access to within QwikGeo.

Tables endpoint is available at `https://api.qwikgeo.com/api/v1/tables`

### Example Output
```json
[
    {
        "id": 1,
        "portal_id": {
            "portal_id": "4c2b7906-ca54-4343-b68b-13fe1a9175af",
            "title": "Tennessee State Parks",
            "created_time": "2022-10-07T14:04:56.224550+00:00",
            "modified_time": "2022-10-07T14:04:56.224643+00:00",
            "tags": [],
            "description": "",
            "views": 4,
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
            ]
        },
        "table_id": "vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps",
        "created_time": "2022-10-07T14:04:56.263222+00:00",
        "modified_time": "2022-10-07T14:04:56.263248+00:00"
    }
]
```

## Table

### Description
The table endpoint returns a table you have access to within QwikGeo.

Table endpoint is available at `https://api.qwikgeo.com/api/v1/tables/{table_id}`

### Example Output
```json
{
    "id": 1,
    "portal_id": {
        "portal_id": "4c2b7906-ca54-4343-b68b-13fe1a9175af",
        "title": "Tennessee State Parks",
        "created_time": "2022-10-07T14:04:56.224550+00:00",
        "modified_time": "2022-10-07T14:04:56.224643+00:00",
        "tags": [],
        "description": "",
        "views": 4,
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
        ]
    },
    "table_id": "vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps",
    "created_time": "2022-10-07T14:04:56.263222+00:00",
    "modified_time": "2022-10-07T14:04:56.263248+00:00"
}
```

## Add Column

### Description
The add column endpoints allows you to add a new column to an existing table in the database.

Add Column endpoint is available at `https://api.qwikgeo.com/api/v1/tables/{table_id}/add_column`

### Example

In the example below, we are adding a column called `test` that is text for the table `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps`.

### Example Input 
```json
{
    "column_name": "test",
    "column_type": "text"
}
```

### Example Output
```json
{
    "status": true
}

```

## Delete Column

### Description
The delete column endpoint allows you to delete a column in an existing table in the database.


Delete Column endpoint is available at `https://api.qwikgeo.com/api/v1/tables/{table_id}/delete_column`

### Example

In the example below, we are deleting a column called `test` from the table `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps`.

### Example Input 
```json
{
    "column_name": "test"
}
```

### Example Output
```json
{
    "status": true
}
```

## Create Table

### Description
The create table endpoints allow you to create a new table inside of a database.

Create Table endpoint is available at `https://api.qwikgeo.com/api/v1/tables/`

### Example

In the example below, we are creating a new table called `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps_new`. We are adding one column in the table called `postalcode`,
and setting the table to have `POINT` geometry.

### Example Input 
```json
{
    "columns": [
        {
            "column_name": "postalcode",
            "column_type": "text"
        }
    ],
    "geometry_type": "POINT"
}
```

### Example Output
```json
{
    "status": true,
    "table_id": "vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps_new"
}
```

## Delete Table

### Description
The delete table endpoint allows you to delete a table within the database.

Delete Table endpoint is available at `https://api.qwikgeo.com/api/v1/tables/{table_id}`

### Example

In the example below, we are deleting a table called `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps`.

### Example Output
```json
{
    "status": true
}
```
