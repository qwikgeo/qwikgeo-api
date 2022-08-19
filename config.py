"""FastGeoPortal App - Configuration File"""

DATABASES = {
    "data": {
        "host": "localhost",
        "database": "geoportal",
        "username": "postgres",
        "password": "postgres",
        "port": 5432,
        "cache_age_in_seconds": 6000,
        "max_features_per_tile": 100000
    }
}
