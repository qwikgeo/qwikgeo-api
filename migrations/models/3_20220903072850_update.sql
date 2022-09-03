-- upgrade --
ALTER TABLE "user" ADD "email" VARCHAR(300);
ALTER TABLE "user" ADD "password_hash" VARCHAR(300);
ALTER TABLE "user" ALTER COLUMN "first_name" SET NOT NULL;
ALTER TABLE "user" ALTER COLUMN "last_name" SET NOT NULL;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "email";
ALTER TABLE "user" DROP COLUMN "password_hash";
ALTER TABLE "user" ALTER COLUMN "first_name" DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN "last_name" DROP NOT NULL;
