CREATE TABLE IF NOT EXISTS Migrations (
    id          SERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Users (
    id          BIGINT NOT NULL PRIMARY KEY,
    banned      BOOLEAN NOT NULL DEFAULT FALSE,
    plevel      BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Guilds (
    id          BIGINT NOT NULL PRIMARY KEY,
    owner_id    BIGINT NOT NULL REFERENCES Users (id),
    plevel      BIGINT NOT NULL DEFAULT 0,
    banned      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS CommandOverride (
    id          SERIAL PRIMARY KEY,
    guild_id    BIGINT NOT NULL REFERENCES Guilds (id) ON DELETE CASCADE,
    cname       VARCHAR(255) NOT NULL,
    isenabled   BOOLEAN NOT NULL,
    otype       VARCHAR(255) NOT NULL,
    otarget     BIGINT NOT NULL,
    ovalue      BOOLEAN NOT NULL
);
