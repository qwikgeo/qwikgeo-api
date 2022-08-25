-- upgrade --
CREATE TABLE IF NOT EXISTS "group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "users" JSONB NOT NULL
);
-- downgrade --
DROP TABLE IF EXISTS "group";
