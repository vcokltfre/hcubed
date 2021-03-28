CREATE TABLE IF NOT EXISTS Reminders (
    id          SERIAL PRIMARY KEY,
    userid      BIGINT NOT NULL REFERENCES Users (id) ON DELETE CASCADE,
    gid         BIGINT NOT NULL REFERENCES Guilds (id) ON DELETE CASCADE,
    cid         BIGINT NOT NULL,
    mid         BIGINT NOT NULL,
    content     VARCHAR(2000) NOT NULL,
    expires     TIMESTAMP NOT NULL,
    expired     BOOLEAN NOT NULL DEFAULT FALSE
);
