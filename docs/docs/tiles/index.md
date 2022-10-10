# Tiles Endpoints

| Method | URL                                                                              | Description                        |
| ------ | -------------------------------------------------------------------------------- | ---------------------------------- |
| `GET`  | `/api/v1/table/tables.json`                                                      | [Tables](#tables)                  |
| `GET`  | `/api/v1/table/{database}/{scheme}/{table}.json`                                 | [Table JSON](#table-json)          |
| `GET`  | `/api/v1/tiles/{database}/{scheme}/{table}/{z}/{x}/{y}.pbf`                      | [Tiles](#tiles)                    |
| `GET`  | `/api/v1/tiles/{database}/{scheme}/{table}.json`                                 | [Table TileJSON](#table-tile-json) |
| `DELETE` | `/api/v1/tiles/cache`                                                          | [Delete Cache](#cache-delete)      |
| `GET`  | `/api/v1/tiles/cache_size`                                                       | [Cache Size](#cache-size)          |


## Tables
Tables endpoint provides a listing of all the tables available to query as vector tiles.


Tables endpoint is available at `/api/v1/table/tables.json`

```shell
curl http://localhost:8000/api/v1/table/tables.json
```

Example Response
```json
[
  {
    "name": "states",
    "schema": "public",
    "type": "table",
    "id": "public.states",
    "database": "data",
    "detailurl": "https://api.qwikgeo.com/api/v1/table/data/public/states.json",
    "viewerurl": "https://api.qwikgeo.com/viewer/data/public/states"
  },
  {},...
```

## Table JSON

Table endpoint is available at `/api/v1/table/{database}/{scheme}/{table}.json`

For example, `states` table in `public` schema in `data` database will be available at `/api/v1/table/data/public/states.json`

```shell
curl http://localhost:8000/api/v1/table/data/public/states.json
```

Example Response
```json
{
  "id": "public.states",
  "schema": "public",
  "tileurl": "https://api.qwikgeo.com/api/v1/tiles/data/public/states/{z}/{x}/{y}.pbf",
  "viewerurl": "https://api.qwikgeo.com/viewer/data/public/states",
  "properties": [
    {
      "name": "gid",
      "type": "integer",
      "description": null
    },
    {
      "name": "geom",
      "type": "geometry",
      "description": null
    },
    {
      "name": "state_name",
      "type": "character varying",
      "description": null
    },
    {
      "name": "state_fips",
      "type": "character varying",
      "description": null
    },
    {
      "name": "state_abbr",
      "type": "character varying",
      "description": null
    },
    {
      "name": "population",
      "type": "integer",
      "description": null
    }
  ],
  "geometrytype": "ST_MultiPolygon",
  "type": "table",
  "minzoom": 0,
  "maxzoom": 22,
  "bounds": [
    -178.2175984,
    18.9217863,
    -66.9692709999999,
    71.406235408712
  ],
  "center": [
    -112.96125695842262,
    45.69082939790446
  ]
}
```

## Tiles

Tiles endpoint is available at `/api/v1/tiles/{database}/{scheme}/{table}/{z}/{x}/{y}.pbf`

For example, `states` table in `public` schema in `data` database will be available at `/api/v1/table/data/public/states/{z}/{x}/{y}.pbf`

### Fields

If you have a table with a large amount of fields you can limit the amount of fields returned using the fields parameter.

#### Note

If you use the fields parameter the tile will not be cached on the server.

For example, if we only want the `state_fips` field.

`/api/v1/table/data/public/states/{z}/{x}/{y}.pbf?fields=state_fips`

### CQL Filtering

CQL filtering is enabled via [pygeofilter](https://pygeofilter.readthedocs.io/en/latest/index.html). This allows you to dynamically filter your tiles database size for larger tiles.

For example, filter the states layer to only show states with a population greater than 1,000,000.

`/api/v1/table/data/public/states/{z}/{x}/{y}.pbf?cql_filter=population>1000000`

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

## Table Tile JSON

Table [TileJSON](https://github.com/mapbox/tilejson-spec) endpoint is available at `/api/v1/tiles/{database}/{scheme}/{table}.json`

For example, `states` table in `public` schema in `data` database will be available at `/api/v1/tiles/data/public/states.json`

```shell
curl http://localhost:8000/api/v1/tiles/data/public/states.json
```

Example Response
```json
{
  "tilejson": "2.2.0",
  "name": "public.states",
  "version": "1.0.0",
  "scheme": "xyz",
  "tiles": [
    "https://api.qwikgeo.com/api/v1/tiles/data/public/states/{z}/{x}/{y}.pbf"
  ],
  "viewerurl": "https://api.qwikgeo.com/viewer/data/public/states",
  "minzoom": 0,
  "maxzoom": 22
}
```

## Cache Delete
The cache delete endpoint allows you to delete any vector tile cache on the server.

This is a DELETE HTTP method endpoint.

In your request you have to pass the following.

```json
{
  "database": "data",
  "scheme": "public",
  "table": "states"
}
```

## Cache Size
Cache Size endpoint allows you to determine the size of a vector tile cache for each table.

```shell
curl http://localhost:8000/api/v1/api/v1/tiles/cache_size
```

Example Response
```json
[
  {
    "table": "data_public_counties",
    "size_in_gigabytes": 0.004711238
  },
  {
    "table": "data_public_states",
    "size_in_gigabytes": 0.000034666
  }
]
```
