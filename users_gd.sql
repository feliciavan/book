CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE gd (
    gd_id SERIAL PRIMARY KEY,
    rating_gd REAL NOT NULL,
    count_gd INTEGER NOT NULL,
    isbn VARCHAR REFERENCES books
);
