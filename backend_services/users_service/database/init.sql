DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'user') THEN
        CREATE USER "user" WITH PASSWORD 'password';
    END IF;
END $$;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users(
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(255) NOT NULL DEFAULT 'normal'
);

CREATE TABLE IF NOT EXISTS sessions(
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(user_id),
    role VARCHAR(255),
    creation_time VARCHAR(255),
    expiration_time VARCHAR(255)
);

INSERT INTO users VALUES (uuid_generate_v4()::VARCHAR, 'admin', MD5('password'), 'admin@email.com', 'maintainer');
