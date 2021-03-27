CREATE TABLE IF NOT EXISTS Restarts (
    id          SERIAL PRIMARY KEY,
    cid         BIGINT NOT NULL,
    mid         BIGINT NOT NULL,
    rsta        TIMESTAMP NOT NULL DEFAULT NOW(),
    done        BOOLEAN NOT NULL DEFAULT FALSE
);
