import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ejpkzfrtfqzuvc:e377f59d6cc3d4994c3428040fd0a45bd9e9943e3a9e904ead4cf851ac476554@ec2-184-73-216-48.compute-1.amazonaws.com:5432/d778rs0msjj172")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    db.execute("CREATE TABLE books (book_id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year VARCHAR NOT NULL)")
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"new book {isbn}")

    db.commit()

if __name__ == "__main__":
    main()
