# Collections Endpoints

| Method | URL                                                                              | Description                             |
| ------ | -------------------------------------------------------------------------------- | ----------------------------------------|
| `GET`  | `/api/v1/collections`                                                       | [Collections](#collections)                  |
| `GET`  | `/api/v1/collections/{name}`                                                | [Collection](#collection)    |
| `GET`  | `/api/v1/collections/{name}/items`                                          | [Items](#items)                        |
| `POST`  | `/api/v1/collections/{name}/items`                                         | [Create Item](#create-item)                        |
| `GET`  | `/api/v1/collections/{name}/items/{id}`                                     | [Item](#item)                          |
| `PUT`  | `/api/v1/collections/{name}/items/{id}`                                     | [Update Item](#update-item)                          |
| `DELETE`  | `/api/v1/collections/{name}/items/{id}`                                  | [Delete Item](#delete-item)                          |
| `PATCH`  | `/api/v1/collections/{name}/items/{id}`                                   | [Modify Item](#modify-item)                          |

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

## Create Item
Create item endpoint allows you to add an item to a collection.

Items endpoint is available at `/api/v1/collections/{item}/items`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.parks/items
```

Example Input
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

Example Response
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

## Update Item
Update item endpoint allows update an item in a collection. You must pass in all properties to update an item.

Items endpoint is available at `/api/v1/collections/{item}/items/{id}`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.parks/items/1
```

Example Input
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

Example Response
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

Items endpoint is available at `/api/v1/collections/{item}/items/{id}`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.parks/items/1
```

Example Response
```json
{
    "status": true
}
```

## Modify Item
Update item endpoint allows update part of an item in a collection. You do not have to pass all properties.

Items endpoint is available at `/api/v1/collections/{item}/items/{id}`

```shell
curl https://api.qwikgeo.com/api/v1/collections/user_data.parks/items/1
```

Example Input
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

Example Response
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