-- upgrade --
CREATE TABLE IF NOT EXISTS "group" (
    "group_id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL UNIQUE
);
COMMENT ON TABLE "group" IS 'Model for group in database';
CREATE TABLE IF NOT EXISTS "groupadmin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(500) NOT NULL,
    "group_id_id" UUID NOT NULL REFERENCES "group" ("group_id") ON DELETE CASCADE
);
COMMENT ON TABLE "groupadmin" IS 'Model for group_user in database';
CREATE TABLE IF NOT EXISTS "groupuser" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(500) NOT NULL,
    "group_id_id" UUID NOT NULL REFERENCES "group" ("group_id") ON DELETE CASCADE
);
COMMENT ON TABLE "groupuser" IS 'Model for group_user in database';
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(500) NOT NULL UNIQUE,
    "password_hash" VARCHAR(300),
    "first_name" VARCHAR(300) NOT NULL,
    "last_name" VARCHAR(300) NOT NULL,
    "photo_url" VARCHAR(1000),
    "email" VARCHAR(500) NOT NULL,
    "created_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "user" IS 'Model for user in database';
CREATE TABLE IF NOT EXISTS "item" (
    "portal_id" UUID NOT NULL  PRIMARY KEY,
    "title" VARCHAR(500) NOT NULL,
    "created_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "tags" JSONB NOT NULL,
    "description" TEXT NOT NULL,
    "views" INT NOT NULL,
    "searchable" BOOL NOT NULL  DEFAULT True,
    "item_type" TEXT NOT NULL,
    "url" TEXT,
    "user_id" VARCHAR(500) NOT NULL REFERENCES "user" ("username") ON DELETE CASCADE
);
COMMENT ON TABLE "item" IS 'Model for item in database';
CREATE TABLE IF NOT EXISTS "itemreadaccesslist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL,
    "portal_id_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE
);
COMMENT ON TABLE "itemreadaccesslist" IS 'Model for item_read_access_list in database';
CREATE TABLE IF NOT EXISTS "itemwriteaccesslist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL,
    "portal_id_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE
);
COMMENT ON TABLE "itemwriteaccesslist" IS 'Model for item_read_access_list in database';
CREATE TABLE IF NOT EXISTS "map" (
    "map_id" UUID NOT NULL  PRIMARY KEY,
    "created_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "pitch" INT NOT NULL  DEFAULT 0,
    "bearing" INT NOT NULL  DEFAULT 0,
    "basemap" VARCHAR(50) NOT NULL,
    "bounding_box" JSONB NOT NULL,
    "item_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE,
    "user_id" VARCHAR(500) NOT NULL REFERENCES "user" ("username") ON DELETE CASCADE
);
COMMENT ON TABLE "map" IS 'Model for map in database';
CREATE TABLE IF NOT EXISTS "layer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "layer_id" VARCHAR(1000) NOT NULL,
    "title" VARCHAR(500) NOT NULL,
    "description" VARCHAR(500) NOT NULL,
    "map_type" VARCHAR(50) NOT NULL,
    "mapbox_name" VARCHAR(50) NOT NULL,
    "geometry_type" VARCHAR(50) NOT NULL,
    "style" JSONB,
    "paint" JSONB,
    "layout" JSONB,
    "fill_paint" JSONB,
    "border_paint" JSONB,
    "bounding_box" JSONB NOT NULL,
    "map_id" UUID NOT NULL REFERENCES "map" ("map_id") ON DELETE CASCADE
);
COMMENT ON TABLE "layer" IS 'Model for layer in database';
CREATE TABLE IF NOT EXISTS "table" (
    "table_id" VARCHAR(50) NOT NULL  PRIMARY KEY,
    "created_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "item_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE,
    "user_id" VARCHAR(500) NOT NULL REFERENCES "user" ("username") ON DELETE CASCADE
);
COMMENT ON TABLE "table" IS 'Model for table in database';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
