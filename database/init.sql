CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE user (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    username VARCHAR(63) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)

CREATE TABLE user_contact (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    "name" VARCHAR(255) NOT NULL,
    email CITEXT UNIQUE NOT NULL, 
    dob DATE NOT NULL,
    ssn_enc BYTEA,
    dek_enc BYTEA,
    user_id UUID REFERENCES user(user_id)
)