CREATE TABLE observation_metadata (
    id VARCHAR(255) PRIMARY KEY,
    observed_on DATE,
    latitude FLOAT,
    longitude FLOAT,
    user_login VARCHAR(255),
    created_at TIMESTAMP,
    name VARCHAR(255),
    preferred_common_name VARCHAR(255),
    native BOOLEAN,
    photo_url TEXT
);
