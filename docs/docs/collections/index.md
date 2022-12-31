# Collections Endpoints

| Method | URL                                                                              | Description                             |
| ------ | -------------------------------------------------------------------------------- | ----------------------------------------|
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections`                              | [Collections](#collections)                  |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}`                       | [Collection](#collection)    |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/items`                 | [Items](#items)                        |
| `POST`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/items`                | [Create Item](#create-item)                        |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`            | [Item](#item)                          |
| `PUT`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`            | [Update Item](#update-item)                          |
| `DELETE`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`         | [Delete Item](#delete-item)                          |
| `PATCH`  | `https:/api.qwikgeo.com/api/v1/collections/table}/items/{id}`          | [Modify Item](#modify-item)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/queryables`          | [Queryables](#queryables)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/tiles`          | [Tiles](#tiles)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}`          | [Tile](#tile)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/metadata`          | [Tiles Metadata](#tiles-metadata)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/tiles/cache_size`          | [Cache Size](#cache-size)                          |
| `DELETE`  | `https:/api.qwikgeo.com/api/v1/collections/{table}/tiles/cache`          | [Delete Cache](#delete-cache)                          |
| `POST`  | `https://api.qwikgeo.com/api/v1/collections/{table_id}/statistics`                                    | [Statistics](#statistics)                   |
| `POST`  | `https://api.qwikgeo.com/api/v1/collections/{table_id}/bins`                                          | [Bins](#bins)                               |
| `POST`  | `https://api.qwikgeo.com/api/v1/collections/{table_id}/numeric_breaks`                                | [Numeric Breaks](#numeric-breaks)           |
| `POST`  | `https://api.qwikgeo.com/api/v1/collections/{table_id}/custom_break_values`                           | [Custom Break Values](#custom-break-values) |
| `GET`   | `https://api.qwikgeo.com/api/v1/collections/{table_id}/autocomplete`                                     | [Table Autocomplete](#table-autocomplete) |

## Endpoint Description's

## Collections
Collection endpoint returns a list of all available tables to query.

Collections endpoint is available at `https:/api.qwikgeo.com/api/v1/collections`

### Example Response
```json
[
    {
        "id": "{table}",
        "title": "zip_centroids",
        "description": "zip_centroids",
        "keywords": [
            "zip_centroids"
        ],
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as JSON",
                "href": "https://api.qwikgeo.com/api/v1/collections/{table}"
            }
        ],
        "geometry": "point",
        "extent": {
            "spatial": {
                "bbox": [
                    -180,
                    -90,
                    180,
                    90
                ],
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "itemType": "feature"
    },
  {},...
```

## Collection
Collection endpoint returns information about a single table.

Collection endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}`

### Example Response
```json
{
    "id": "{table}",
    "title": "Zip Centroids",
    "description": "",
    "keywords": [],
    "links": [
        {
            "type": "application/geo+json",
            "rel": "self",
            "title": "Items as GeoJSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/items"
        },
        {
            "type": "application/json",
            "rel": "queryables",
            "title": "Queryables for this collection as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/queryables"
        },
        {
            "type": "application/json",
            "rel": "tiles",
            "title": "Tiles as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/tiles"
        }
    ],
    "geometry": "point",
    "extent": {
        "spatial": {
            "bbox": [
                -180,
                -90,
                180,
                90
            ],
            "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
        }
    },
    "itemType": "feature"
}
```

## Items
Items endpoint returns a geojson feature collection for a collection.

Items endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}/items`

### Parameters
* `bbox=mix,miny,maxx,maxy` - filter features in response to ones intersecting a bounding box (in lon/lat or specified CRS). Ex. `17,-48,69,-161`
* `<propname>=val` - filter features for a property having a value.
  Multiple property filters are ANDed together.
* `filter=cql-expr` - filters features via a CQL expression.
* `properties=PROP-LIST`- return only specific properties (comma-separated).
  If PROP-LIST is empty, no properties are returned.
  If not present, all properties are returned.dinates to use N decimal places
* `sortby=PROP` - sort the response items by a property.
* `sortdesc=1` - sort the response items by ascending or descending. Default desc
* `limit=N` - limits the number of features in the response.
* `offset=N` - starts the response at an offset.
* `return_geometry=bool` - Boolean to determine if geometry should be returned with response.
* `srid=srid_number` - The srid number for data. Default is 4326.

### Example Response
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    ...
                ]
            },
            "properties": {
                "gid": 5,
                "state_name": "Nevada",
                "state_fips": "32",
                "sub_region": "Mountain",
                "state_abbr": "NV",
                "population": 2994047
            },
            "id": 1
        },
        ...
    ],
    "numberMatched": 57,
    "numberReturned": 10,
    "links": [
        {
            "type": "application/geo+json",
            "rel": "self",
            "title": "This document as GeoJSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/items"
        },
        {
            "type": "application/json",
            "title": "States",
            "rel": "collection",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}"
        },
        {
            "type": "application/geo+json",
            "rel": "next",
            "title": "items (next)",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/items?offfset=10"
        }
    ]
}
```

## Create Item
Create item endpoint allows you to add an item to a collection.

Create Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}/items`

### Example Input
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "objectid": 45,  
        "manage_area": 2,
        "am_first_name": "Ryan",
        "am_last_name": "Forbess",
        "am_title": "Area Manager",
        "am_email": "Ryan.Forbess@tn.gov",
        "am_phone": "731-358-9724",
        "pm_first_name": "Michael",
        "pm_last_name": "Beasley",
        "pm_email": "Michael.Beasley@tn.gov",
        "pm_title": "Park Manager 1",
        "pm_phone": "731-253-9652",
        "park_name": "Big Cypress Tree State Park",
        "tsp_uid": "TSP-0314"
    }
}
```

### Example Response
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "objectid": 45,  
        "manage_area": 2,
        "am_first_name": "Ryan",
        "am_last_name": "Forbess",
        "am_title": "Area Manager",
        "am_email": "Ryan.Forbess@tn.gov",
        "am_phone": "731-358-9724",
        "pm_first_name": "Michael",
        "pm_last_name": "Beasley",
        "pm_email": "Michael.Beasley@tn.gov",
        "pm_title": "Park Manager 1",
        "pm_phone": "731-253-9652",
        "park_name": "Big Cypress Tree State Park",
        "tsp_uid": "TSP-0314"
    },
    "id": 63
}
```

## Item

Item endpoint returns a geojson feature collection for a single feature in a collection.

Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`

### Parameters
* `properties=PROP-LIST`- return only specific properties (comma-separated).
  If PROP-LIST is empty, no properties are returned.
  If not present, all properties are returned.
* `return_geometry=bool` - Boolean to determine if geometry should be returned with response.

### Example Response
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    ...
                ]
            },
            "properties": {
                "gid": 5,
                "state_name": "Nevada",
                "state_fips": "32",
                "sub_region": "Mountain",
                "state_abbr": "NV",
                "population": 2994047
            },
            "id": 1,
            "links": [
                {
                    "type": "application/geo+json",
                    "rel": "self",
                    "title": "This document as GeoJSON",
                    "href": "https://api.qwikgeo.com/api/v1/collections/{table}/items/{id}"
                },
                {
                    "type": "application/geo+json",
                    "title": "items as GeoJSON",
                    "rel": "items",
                    "href": "https://api.qwikgeo.com/api/v1/collections/{table}/items"
                },
                {
                    "type": "application/json",
                    "title": "States",
                    "rel": "collection",
                    "href": "https://api.qwikgeo.com/api/v1/collections/{table}"
                }
            ]
        }
    ]
}
```

## Update Item
Update item endpoint allows update an item in a collection. You must pass in all properties to update an item.

Update Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`

### Example Input
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "objectid": 45,  
        "manage_area": 2,
        "am_first_name": "Ryan",
        "am_last_name": "Forbess",
        "am_title": "Area Manager",
        "am_email": "Ryan.Forbess@tn.gov",
        "am_phone": "731-358-9724",
        "pm_first_name": "Michael",
        "pm_last_name": "Beasley",
        "pm_email": "Michael.Beasley@tn.gov",
        "pm_title": "Park Manager 1",
        "pm_phone": "731-253-9652",
        "park_name": "Big Cypress Tree State Park",
        "tsp_uid": "TSP-0314"
    },
    "id": 1
}
```

### Example Response
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "objectid": 45,  
        "manage_area": 2,
        "am_first_name": "Ryan",
        "am_last_name": "Forbess",
        "am_title": "Area Manager",
        "am_email": "Ryan.Forbess@tn.gov",
        "am_phone": "731-358-9724",
        "pm_first_name": "Michael",
        "pm_last_name": "Beasley",
        "pm_email": "Michael.Beasley@tn.gov",
        "pm_title": "Park Manager 1",
        "pm_phone": "731-253-9652",
        "park_name": "Big Cypress Tree State Park",
        "tsp_uid": "TSP-0314"
    },
    "id": 1
}
```

## Delete Item
Delete item endpoint allows delete an item in a collection.

Delete Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{table}/items/{id}`

### Example Response
```json
{
    "status": true
}
```

## Modify Item
Modify item endpoint allows update part of an item in a collection. You do not have to pass all properties.

Modify Item endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/items/{id}`

### Example Input
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "park_name": "Big Cypress Tree State Park (New)"
    },
    "id": 1
}
```

### Example Response
```json
{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [
            -88.8892,
            36.201015
        ]
    },
    "properties": {      
        "park_name": "Big Cypress Tree State Park (New)",
    },
    "id": 1
}
```

## Queryables
Queryables endpoint allows you to see queryable information about a collection.

Queryables endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/queryables`

### Example Response
```json
{
    "$id": "https://api.qwikgeo.com/api/v1/collections/{table}/queryables",
    "title": "Tennessee State Parks",
    "type": "object",
    "$schema": "http://json-schema.org/draft/2019-09/schema",
    "properties": {
        "objectid": {
            "title": "objectid",
            "type": "numeric"
        },
        "manage_area": {
            "title": "manage_area",
            "type": "numeric"
        },
        "gid": {
            "title": "gid",
            "type": "numeric"
        }
    }
}
```

## Tiles
Tiles endpoint allows you to get information about generating tiles for a collection.

Tiles endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/tiles`

### Example Response
```json
{
    "id": "{table}",
    "title": "Tennessee State Parks",
    "description": "",
    "links": [
        {
            "type": "application/json",
            "rel": "self",
            "title": "This document as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/tiles"
        },
        {
            "type": "application/vnd.mapbox-vector-tile",
            "rel": "item",
            "title": "This collection as Mapbox vector tiles",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
            "templated": true
        },
        {
            "type": "application/json",
            "rel": "describedby",
            "title": "Metadata for this collection in the TileJSON format",
            "href": "https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/metadata",
            "templated": true
        }
    ],
    "tileMatrixSetLinks": [
        {
            "tileMatrixSet": "WorldCRS84Quad",
            "tileMatrixSetURI": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json"
        }
    ]
}
```

## Tile

Tile endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}`

### Fields

If you have a table with a large amount of fields you can limit the amount of fields returned using the fields parameter.

#### Note

If you use the fields parameter the tile will not be cached on the server.

For example, if we only want the `state_fips` field.

`https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}?fields=state_fips`

### CQL Filtering

CQL filtering is enabled via [pygeofilter](https://pygeofilter.readthedocs.io/en/latest/index.html). This allows you to dynamically filter your tiles database size for larger tiles.

For example, filter the states layer to only show states with a population greater than 1,000,000.

`https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}?cql_filter=population>1000000`

[Geoserver](https://docs.geoserver.org/stable/en/user/tutorials/cql/cql_tutorial.html) has examples of using cql filters.

#### Spatial Filters

| Filters | 
| --- |
| Intersects |
| Equals |
| Disjoint |
| Touches |
| Within |
| Overlaps |
| Crosses |
| Contains |

#### Note

If you use the cql_filter parameter the tile will not be cached on the server.

## Tiles Metadata
Tiles metadata endpoint allows you to get information about tiles for a collection.

Tiles endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/tiles/{tile_matrix_set_id}/metadata`

### Example Response
```json
{
    "tilejson": "3.0.0",
    "name": "{table}",
    "tiles": "https://api.qwikgeo.com/api/v1/collections/{table}/tiles/WorldCRS84Quad/{tile_matrix}/{tile_row}/{tile_col}?f=mvt",
    "minzoom": "0",
    "maxzoom": "22",
    "attribution": null,
    "description": "",
    "vector_layers": [
        {
            "id": "{table}",
            "description": "",
            "minzoom": 0,
            "maxzoom": 22,
            "fields": {
                "objectid": "numeric",
                "manage_area": "numeric",
                "gid": "numeric"
            }
        }
    ]
}
```

## Cache Size
Cache Size endpoint allows you to determine the size of a vector tile cache for each table.

Cache Size endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/tiles/cache_size`

Example Response
```json
{
  "size_in_gigabytes": 0.004711238
}
```

## Delete Cache
The delete cache endpoint allows you to delete any vector tile cache on the server.

Delete Cache endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table}/tiles/cache`

### Example Response
```json
{
  "size_in_gigabytes": 0.004711238
}
```

## Statistics

### Description
The statistics endpoints allows you to perform a multitude of common math statistics on your table such as `'distinct', 'avg', 'count', 'sum', 'max', 'min'`.

Statistics endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table_id}/statistics`

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

### Example

In the example below we will be searching for the number of parcels, average deed ac, and distinct first names filtered by last name of `DOOLEY`.

### Example Input 
```json
{
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

Bins endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table_id}/bins`

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

### Example

Calculate 10 bins for the `deed_ac` column on the `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps_new` table.

### Example Input
```json
{
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

Numeric Breaks endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table_id}/numeric_breaks`

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

### Example

Create 3 breaks based off of the column `population` for the table `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps` using a quantile break type.

### Example Input
```json
{
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

Custom Break Values endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{table_id}/custom_break_values`

### Parameters
* `coordinates=coords` - a list of coordinates used to filter the response
* `geometry_type=geom_type` - The type of geometry from the coordinates parameters. Options: `'POINT', 'LINESTRING', 'POLYGON'`
* `spatial_relationship=relationship` - The type of spatial query to perform with the coordinates parameters. Options: `'ST_Intersects', 'ST_Crosses', 'ST_Within', 'ST_Contains', 'ST_Overlaps', 'ST_Disjoint', 'ST_Touches'`
* `filter=cql-expr` - filters features via a CQL expression.

### Example

Create 3 custom bins `0 - 1,000`, `1,000 - 9,000`, and `9,000 - 140,000` based 
off of the column `population` for the table `vccvnkvhrmzsqqbbcacvjrlspfpdhbcthvjszbnfledgklxnps` using a quantile break type.

### Example Input
```json
{
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

### Example

Search for possible park names in Tennessee that contain `bi`.

### Example Input
```shell
curl https://api.qwikgeo.com/api/v1/collections/{table_id}/autocomplete?q=bi&column=park_name
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
