-- upgrade --
ALTER TABLE "user" ADD "photo_url" VARCHAR(1000);
ALTER TABLE "user" ADD "first_name" VARCHAR(300);
ALTER TABLE "user" ADD "last_name" VARCHAR(300);
ALTER TABLE "user" DROP COLUMN "name";
ALTER TABLE "user" DROP COLUMN "password_hash";
-- downgrade --
ALTER TABLE "user" ADD "name" VARCHAR(50);
ALTER TABLE "user" ADD "password_hash" VARCHAR(128) NOT NULL;
ALTER TABLE "user" DROP COLUMN "photo_url";
ALTER TABLE "user" DROP COLUMN "first_name";
ALTER TABLE "user" DROP COLUMN "last_name";
