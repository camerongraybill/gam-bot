-- upgrade --
CREATE TABLE IF NOT EXISTS "gamuser" (
    "discord_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "gam_coins" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
