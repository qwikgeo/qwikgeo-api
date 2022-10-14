# Collections Endpoints

| Method | URL                                                                              | Description                             |
| ------ | -------------------------------------------------------------------------------- | ----------------------------------------|
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections`                              | [Collections](#collections)                  |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}`                       | [Collection](#collection)    |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items`                 | [Items](#items)                        |
| `POST`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items`                | [Create Item](#create-item)                        |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`            | [Item](#item)                          |
| `PUT`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`            | [Update Item](#update-item)                          |
| `DELETE`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`         | [Delete Item](#delete-item)                          |
| `PATCH`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.table}/items/{id}`          | [Modify Item](#modify-item)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables`          | [Queryables](#queryables)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles`          | [Tiles](#tiles)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}`          | [Tile](#tile)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/metadata`          | [Tiles Metadata](#tiles-metadata)                          |
| `GET`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/cache_size`          | [Cache Size](#cache-size)                          |
| `DELETE`  | `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/cache`          | [Delete Cache](#delete-cache)                          |

## Endpoint Description's

## Collections
Collection endpoint returns a list of all available tables to query.

Collections endpoint is available at `https:/api.qwikgeo.com/api/v1/collections`

### Example Response
```json
[
    {
        "id": "{scheme}.{table}",
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
                "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
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

Collection endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}`

### Example Response
```json
{
    "id": "{scheme}.{table}",
    "title": "Zip Centroids",
    "description": "",
    "keywords": [],
    "links": [
        {
            "type": "application/geo+json",
            "rel": "self",
            "title": "Items as GeoJSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
        },
        {
            "type": "application/json",
            "rel": "queryables",
            "title": "Queryables for this collection as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables"
        },
        {
            "type": "application/json",
            "rel": "tiles",
            "title": "Tiles as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles"
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

Items endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items`

### Parameters
* `bbox=mix,miny,maxx,maxy` - filter features in response to ones intersecting a bounding box (in lon/lat or specified CRS). Ex. `17,-48,69,-161`
* `<propname>=val` - filter features for a property having a value.
  Multiple property filters are ANDed together.
* `filter=cql-expr` - filters features via a CQL expression.
* `properties=PROP-LIST`- return only specific properties (comma-separated).
  If PROP-LIST is empty, no properties are returned.
  If not present, all properties are returned.dinates to use N decimal places
* `sortby=PROP[A|D]` - sort the response items by a property (ascending (default) or descending).
* `limit=N` - limits the number of features in the response.
* `offset=N` - starts the response at an offset.
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
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
        },
        {
            "type": "application/json",
            "title": "States",
            "rel": "collection",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
        },
        {
            "type": "application/geo+json",
            "rel": "next",
            "title": "items (next)",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items?offfset=10"
        }
    ]
}
```

## Create Item
Create item endpoint allows you to add an item to a collection.

Create Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items`

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

Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`

### Parameters
* `properties=PROP-LIST`- return only specific properties (comma-separated).
  If PROP-LIST is empty, no properties are returned.
  If not present, all properties are returned.

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
                    "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}"
                },
                {
                    "type": "application/geo+json",
                    "title": "items as GeoJSON",
                    "rel": "items",
                    "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items"
                },
                {
                    "type": "application/json",
                    "title": "States",
                    "rel": "collection",
                    "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}"
                }
            ]
        }
    ]
}
```

## Update Item
Update item endpoint allows update an item in a collection. You must pass in all properties to update an item.

Update Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`

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

Delete Item endpoint is available at `https:/api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`

### Example Response
```json
{
    "status": true
}
```

## Modify Item
Modify item endpoint allows update part of an item in a collection. You do not have to pass all properties.

Modify Item endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/items/{id}`

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

Queryables endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables`

### Example Response
```json
{
    "$id": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/queryables",
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

Tiles endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles`

### Example Response
```json
{
    "id": "{scheme}.{table}",
    "title": "Tennessee State Parks",
    "description": "",
    "links": [
        {
            "type": "application/json",
            "rel": "self",
            "title": "This document as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles"
        },
        {
            "type": "application/vnd.mapbox-vector-tile",
            "rel": "item",
            "title": "This collection as Mapbox vector tiles",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
            "templated": true
        },
        {
            "type": "application/json",
            "rel": "describedby",
            "title": "Metadata for this collection in the TileJSON format",
            "href": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/metadata",
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

Tile endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}`

### Fields

If you have a table with a large amount of fields you can limit the amount of fields returned using the fields parameter.

#### Note

If you use the fields parameter the tile will not be cached on the server.

For example, if we only want the `state_fips` field.

`https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}?fields=state_fips`

### CQL Filtering

CQL filtering is enabled via [pygeofilter](https://pygeofilter.readthedocs.io/en/latest/index.html). This allows you to dynamically filter your tiles database size for larger tiles.

For example, filter the states layer to only show states with a population greater than 1,000,000.

`https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}?cql_filter=population>1000000`

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

Tiles endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/{tile_matrix_set_id}/metadata`

### Example Response
```json
{
    "tilejson": "3.0.0",
    "name": "{scheme}.{table}",
    "tiles": "https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/WorldCRS84Quad/{tile_matrix}/{tile_row}/{tile_col}?f=mvt",
    "minzoom": "0",
    "maxzoom": "22",
    "attribution": null,
    "description": "",
    "vector_layers": [
        {
            "id": "{scheme}.{table}",
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

Cache Size endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/cache_size`

Example Response
```json
{
  "size_in_gigabytes": 0.004711238
}
```

## Delete Cache
The delete cache endpoint allows you to delete any vector tile cache on the server.

Delete Cache endpoint is available at `https://api.qwikgeo.com/api/v1/collections/{scheme}.{table}/tiles/cache`

### Example Response
```json
{
  "size_in_gigabytes": 0.004711238
}
```


