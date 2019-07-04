CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    reviewer VARCHAR NOT NULL,
    review VARCHAR NOT NULL,
    book_id INTEGER REFERENCES books,
    user_id INTEGER REFERENCES users
);
