-- upgrade --
CREATE TABLE IF NOT EXISTS "group" (
    "group_id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "groupuser" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(500) NOT NULL,
    "group_id_id" UUID NOT NULL REFERENCES "group" ("group_id") ON DELETE CASCADE
);
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
    "url" TEXT
);
CREATE TABLE IF NOT EXISTS "itemreadaccesslist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL,
    "portal_id_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "itemwriteaccesslist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(500) NOT NULL,
    "portal_id_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "table" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "table_id" VARCHAR(50) NOT NULL,
    "created_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "portal_id_id" UUID NOT NULL REFERENCES "item" ("portal_id") ON DELETE CASCADE
);
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
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
