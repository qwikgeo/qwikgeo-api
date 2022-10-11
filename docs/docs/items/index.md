# Items Endpoints

| Method | URL                                                                              | Description                                 |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------- |
| `POST`  | `/api/v1/items/tables/add_column`                                                     | [Add Column](#add-column)                   |
| `DELETE`  | `/api/v1/items/tables/delete_column`                                                | [Delete Column](#delete-column)             |
| `POST`  | `/api/v1/items/tables/add_row`                                                        | [Add Row](#add-row)                         |
| `DELETE`  | `/api/v1/items/tables/delete_row`                                                   | [Delete Row](#delete-row)                   |
| `DELETE`  | `/api/v1/items/tables/delete_table`                                                 | [Delete Table](#delete-table)               |
| `POST`  | `/api/v1/items/tables/create_table`                                                   | [Create Table](#create-table)               |
| `POST`  | `/api/v1/items/tables/statistics`                                                     | [Statistics](#statistics)                   |
| `POST`  | `/api/v1/items/tables/bins`                                                           | [Bins](#bins)                               |
| `POST`  | `/api/v1/items/tables/numeric_breaks`                                                 | [Numeric Breaks](#numeric-breaks)           |
| `POST`  | `/api/v1/items/tables/custom_break_values`                                            | [Custom Break Values](#custom-break-values) |
| `GET`   | `/api/v1/items/tables/table/{table}/autocomplete`                                      | [Table Autocomplete](#table-autocomplete) |

## Endpoint Description's

## Edit Row Attributes

### Description
Edit Row Attributes endpoint allows you to edit one/all atrributes for a row at a time.
In the example below we are changing the `objectid` and `last_name` columns for the row with a gid of `1`.


Example: 
### Example Input 
```json
{
    "table": "mclean_county_parcels",
    "gid": 1,
    "values": {
        "objectid": "1",
        "last_name": "sample"
    }
}
```

### Example Output
```json
{
    "status": true
}
```

## Edit Row Geometry

### Description
Edit Row Geometry endpoint allows you to change the geometry for each feature in a table by passing in geojson geometry in SRID 4326.
In the example below, we are updating the table called `zip_centroids` with the gid of `1` for a new lat lng of `[-88.23456,40.12345]`.

Example: 
### Example Input 
```json
{
    "table": "zip_centroids",
    "gid": 1,
    "geojson": {
        "type": "Point",
        "coordinates": [
            -88.23456,
            40.12345
        ]
    }
}
```

### Example Output
```json
{
    "status": true
}
```

## Add Column

### Description
The add column endpoints allows you to add a new column to an existing table in the database.

Example: In the example below, we are adding a column called `test` that is text for the table `zip_centroids`.

### Example Input 
```json
{
    "table": "zip_centroids",
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

Example: In the example below, we are deleting a column called `test` from the table `zip_centroids`.

### Example Input 
```json
{
    "table": "zip_centroids",
    "column_name": "test"
}
```

### Example Output
```json
{
    "status": true
}
```

## Add Row

### Description
The add row endpoint allows you to add a new to an existing table within the database. 
You can pass in one or all columns for this endpoint. If you do not pass in a column the value will be null.

Example: In the example below, we are adding a a new row to the `zip_centroids` table and only adding the postalcode column with the geometry.

### Example Input 
```json
{
    "table": "zip_centroids",
    "columns": [
        {
            "column_name": "postalcode",
            "value": "55555"
        }
    ],
    "geojson": {
        "type": "Point",
        "coordinates": [
            -88.23456,
            40.12345
        ]
    }
}
```

### Example Output
```json
{
    "status": true,
    "gid": 7821
}
```
## Delete Row

### Description
The delete row endpoint allows you to delete a row for a table that exists in the database.

Example: In the example below, we are deleting the column with a gid of `1` in the table `zip_centroids`.

### Example Input 
```json
{
    "table": "zip_centroids",
    "gid": 1
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

Example: In the example below, we are creating a new table called `zip_centroids_new`. We are adding one column in the table called `postalcode`,
and setting the table to have `POINT` geometry.

### Example Input 
```json
{
    "table": "zip_centroids_new",
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
    "status": true
}
```

## Delete Table

### Description
The delete table endpoint allows you to delete a table within the database.

Example: In the example below, we are deleting a table called `zip_centroids`.

### Example Input 
```json
{
    "table": "zip_centroids"
}
```

### Example Output
```json
{
    "status": true
}
```

## Statistics

### Description
The statistics endpoints allows you to perform a multitude of common math statistics on your table such as `'distinct', 'avg', 'count', 'sum', 'max', 'min'`.

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

Example: In the example below we will be searching for the number of parcels, average deed ac, and distinct first names filtered by last name of `DOOLEY`.

### Example Input 
```json
{
    "table": "mclean_county_parcels",
    "aggregate_columns": [
        {
            "type": "count",
            "column": "gid"
        },
        {
            "type": "avg",
            "column": "deed_ac"
        },
        {
            "type": "distinct",
            "column": "first_name",
            "group_column": "first_name",
            "group_method": "count"
        }
    ],
    "filter": "last_name LIKE '%DOOLEY%'"
}
```

### Example Output
```json
{
    "results": {
        "count_gid": 19,
        "avg_deed_ac": 64.28666666666666,
        "distinct_first_name_count_first_name": [
            {
                "first_name": "",
                "count": 3
            },
            {
                "first_name": "COLE",
                "count": 3
            },
            {
                "first_name": "% BAS",
                "count": 2
            },
            {
                "first_name": "%FIRST MID AG SERVICES ",
                "count": 2
            },
            {
                "first_name": "COLE & WENDY",
                "count": 1
            },
            {
                "first_name": "EDITH",
                "count": 1
            },
            {
                "first_name": "JAMES R & TERESA",
                "count": 1
            },
            {
                "first_name": "KENNETH",
                "count": 1
            },
            {
                "first_name": "KEVIN",
                "count": 1
            },
            {
                "first_name": "LUCAS",
                "count": 1
            },
            {
                "first_name": "MCCALLA O & DEANA J",
                "count": 1
            },
            {
                "first_name": "THOMAS",
                "count": 1
            },
            {
                "first_name": "WENDY",
                "count": 1
            }
        ]
    },
    "status": "SUCCESS"
}
```

## Bins

### Description

The bins endpoints allows you to help visualize the spread of a data for a numerical column.

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

Example: Calculate 10 bins for the `deed_ac` column on the `mclean_county_parcels` table.

### Example Input
```json
{
    "table": "mclean_county_parcels",
    "column": "deed_ac",
    "bins": 10
}
```

### Example Output
```json
{
    "results": [
        {
            "min": 0.0,
            "max": 145.158,
            "count": 15993
        },
        {
            "min": 145.158,
            "max": 290.316,
            "count": 1088
        },
        {
            "min": 290.316,
            "max": 435.47399999999993,
            "count": 116
        },
        {
            "min": 435.47399999999993,
            "max": 580.632,
            "count": 19
        },
        {
            "min": 580.632,
            "max": 725.79,
            "count": 11
        },
        {
            "min": 725.79,
            "max": 870.9479999999999,
            "count": 1
        },
        {
            "min": 870.9479999999999,
            "max": 1016.1059999999999,
            "count": 0
        },
        {
            "min": 1016.1059999999999,
            "max": 1161.264,
            "count": 0
        },
        {
            "min": 1161.264,
            "max": 1306.4219999999998,
            "count": 0
        },
        {
            "min": 1306.4219999999998,
            "max": 1451.58,
            "count": 1
        }
    ],
    "status": "SUCCESS"
}
```

## Numeric Breaks

### Description
Create bins of data based off of different mathmatical break types.

Break Types: `equal_interval, head_tail, quantile, jenk`.

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

Example: Create 3 breaks based off of the column `population` for the table `zip_centroids` using a quantile break type.

### Example Input
```json
{
    "table": "zip_centroids",
    "column": "population",
    "number_of_breaks": 3,
    "break_type": "quantile"
}
```

### Example Output
```json
{
    "results": [
        {
            "min": 0,
            "max": 1470,
            "count": 10301
        },
        {
            "min": 1470,
            "max": 8932,
            "count": 10373
        },
        {
            "min": 8932,
            "max": 133324,
            "count": 10377
        }
    ],
    "status": "SUCCESS"
}
```

## Custom Break Values

### Description
Create bins based off of your own min and max ranges and provide a count back for each bin.

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

Example: Create 3 custom bins `0 - 1,000`, `1,000 - 9,000`, and `9,000 - 140,000` based 
off of the column `population` for the table `zip_centroids` using a quantile break type.

### Example Input
```json
{
    "table": "zip_centroids",
    "column": "population",
    "breaks": [
        {
            "min": 0,
            "max": 1000
        },
        {
            "min": 1000,
            "max": 9000
        },
        {
            "min": 9000,
            "max": 140000
        }
    ]
}
```

### Example Output
```json
{
    "results": [
        {
            "min": 0.0,
            "max": 1000.0,
            "count": 7981
        },
        {
            "min": 1000.0,
            "max": 9000.0,
            "count": 12720
        },
        {
            "min": 9000.0,
            "max": 140000.0,
            "count": 10350
        }
    ],
    "status": "SUCCESS"
}
```

## Table Autocomplete

### Description
Return a list of possible values from a column in a table in alphabetical order.

### Parameters
* `q=q` - The search term used when performing a lookup
* `column=column` - Name of the column to perform lookup against

Example: Search for possible park names in Tennessee that contain `bi`.

### Example Input
```shell
curl https://api.qwikgeo.com/api/v1/items/tables/table/{table}/autocomplete?q=bi&column=park_name
```

### Example Output
```json
[
    "Bicentennial Capitol Mall State Park",
    "Big Cypress Tree State Park",
    "Big Hill Pond State Park",
    "Big Ridge State Park",
    "Cordell Hull Birthplace State Park",
    "David Crockett Birthplace State Park",
    "Seven Islands State Birding Park"
]
```