# Collections Endpoints

| Method | URL                                                                              | Description                             |
| ------ | -------------------------------------------------------------------------------- | ----------------------------------------|
| `GET`  | `/api/v1/collections`                                                       | [Collections](#collections)                  |
| `GET`  | `/api/v1/collections/{name}`                                                | [Collection](#collection)    |
| `GET`  | `/api/v1/collections/{name}/items`                                          | [Items](#items)                        |
| `GET`  | `/api/v1/collections/{name}/items/{id}`                                     | [Item](#item)                          |

## Endpoint Description's

## Collections
Collection endpoint returns a list of all available tables to query.

Collections endpoint is available at `/api/v1/collections`

```shell
curl https://api.qwikgeo.com/api/v1/collections
```

Example Response
```json
[
    {
        "id": "user_data.zip_centroids",
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
                "href": "https://api.qwikgeo.com/api/v1/collections/user_data.zip_centroids"
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

Collections endpoint is available at `/api/v1/collections/{item}`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.zip_centroids
```

Example Response
```json
{
    "id": "user_data.zip_centroids",
    "title": "Zip Centroids",
    "description": "",
    "keywords": [],
    "links": [
        {
            "type": "application/json",
            "rel": "self",
            "title": "Items as GeoJSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/user_data.zip_centroids/items"
        },
        {
            "type": "application/json",
            "rel": "queryables",
            "title": "Queryables for this collection as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/user_data.zip_centroids/queryables"
        },
        {
            "type": "application/json",
            "rel": "tiles",
            "title": "Tiles as JSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/user_data.zip_centroids/tiles"
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

Items endpoint is available at `/api/v1/collections/{item}/items`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.states/items
```

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

Example Response
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
    "numberReturned": 1,
    "links": [
        {
            "type": "application/json",
            "rel": "self",
            "title": "This document as GeoJSON",
            "href": "https://api.qwikgeo.com/api/v1/collections/user_data.states/items"
        },
        {
            "type": "application/json",
            "title": "States",
            "rel": "collection",
            "href": "https://api.qwikgeo.com/api/v1/collections/user_data.states"
        }
    ]
}
```

## Item

Item endpoint returns a geojson feature collection for a single feature in a collection.

Item endpoint is available at `/api/v1/collections/{item}/items/{id}`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.states/items/5
```

### Parameters
* `properties=PROP-LIST`- return only specific properties (comma-separated).
  If PROP-LIST is empty, no properties are returned.
  If not present, all properties are returned.

Example Response
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
                    "type": "application/json",
                    "rel": "self",
                    "title": "This document as GeoJSON",
                    "href": "https://api.qwikgeo.com/api/v1/collections/user_data.states/items/1"
                },
                {
                    "type": "application/json",
                    "title": "items as GeoJSON",
                    "rel": "items",
                    "href": "https://api.qwikgeo.com/api/v1/collections/user_data.states/items"
                },
                {
                    "type": "application/json",
                    "title": "States",
                    "rel": "collection",
                    "href": "https://api.qwikgeo.com/api/v1/collections/user_data.states"
                }
            ]
        }
    ]
}
```
