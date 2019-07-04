import os
import requests
import json

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not ("postgres://ejpkzfrtfqzuvc:e377f59d6cc3d4994c3428040fd0a45bd9e9943e3a9e904ead4cf851ac476554@ec2-184-73-216-48.compute-1.amazonaws.com:5432/d778rs0msjj172"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://ejpkzfrtfqzuvc:e377f59d6cc3d4994c3428040fd0a45bd9e9943e3a9e904ead4cf851ac476554@ec2-184-73-216-48.compute-1.amazonaws.com:5432/d778rs0msjj172")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def login():
    """Check whether a user is legitmate and in the current user database."""
    # Get form information.
    try:
        name = request.form.get("name")
        password = request.form.get("password")

        # Make sure the user exists.
        if name:
            if db.execute("SELECT * FROM users WHERE name = :name", {"name":name}).rowcount == 0:
                return render_template("error.html", message="You have not signed up yet.")
            else:
                pwd = db.execute("SELECT password FROM users WHERE name = :name", {"name":name}).fetchall()
                pwd = pwd[0][0]
                if pwd == password:
                    id = db.execute("SELECT user_id FROM users WHERE name = :name", {"name":name}).fetchall()
                    id = id[0][0]
                    session["user_id"]=id
                    return render_template("search.html")
                else:
                    return render_template("error.html", message="wrong password")
        else:
            return render_template("error.html", message="no input")
    except:
        return render_template("error.html", message="no input")

@app.route("/signup")
def signup():
    """A new user is signing up."""
    return render_template("signup.html")

@app.route("/signin", methods=["POST"])
def signin():
    # Get form information.
    name = request.form.get("name")
    password = request.form.get("password")

    # Make sure the new user does not exist.
    if db.execute("SELECT * FROM users WHERE name = :name", {"name":name}).rowcount != 0:
        return render_template("error.html", message="User name already exists.")
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",
            {"name":name, "password": password})
    db.commit()
    id = db.execute("SELECT user_id FROM users WHERE name = :name", {"name":name}).fetchall()
    id = id[0][0]
    session["user_id"]=id
    return render_template("search.html")

@app.route("/results", methods=["POST"])
def results():
    # Get form information.
    search = request.form.get("search")
    if search:
        partial='%'+search+'%'

        result = db.execute("SELECT * FROM books WHERE isbn LIKE :partial OR title LIKE :partial OR author LIKE :partial OR year LIKE :partial" ,{"partial":partial}).fetchone()
        if result is None:
            return render_template("error.html", message="No such book.")

        # Get all results.
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :partial OR title LIKE :partial OR author LIKE :partial OR year LIKE :partial" ,{"partial":partial}).fetchall()
        return render_template("list.html", results=results, search=search)
    else:
        return render_template("error.html", message="no input")


@app.route("/results/<int:book_id>", methods=["GET", "POST"])
def result(book_id):

    book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchone()

    # Initialize reviews to avoid error

    if request.method == "POST":
        user_id = session.get("user_id")
        track = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id=:book_id", {"user_id": user_id, "book_id": book_id}).fetchall()
        if not track:
            try:
                rating = float(request.form.get("rating"))
                if rating < 1 or rating > 5:
                    return render_template("error.html", message="Rating exceeds the range.")
                else:
                    review = request.form.get("review")
                    reviewer = db.execute("SELECT name FROM users WHERE user_id = :user_id", {"user_id": user_id}).fetchall()
                    reviewer = reviewer[0][0]
                    db.execute("INSERT INTO reviews (book_id, rating, review, user_id, reviewer) VALUES (:book_id, :rating, :review, :user_id, :reviewer)",
                                {"book_id": book_id, "rating": rating, "review": review, "user_id": user_id, "reviewer": reviewer})
                    db.commit()
            except:
                return render_template("error.html", message="wrong input")
        else:

                return render_template("error.html", message="You have already commented.")

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    isbn = db.execute("SELECT isbn FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    isbn = isbn[0][0]
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "MMaRO0RhU3TAVsf60kU9lw", "isbns": isbn})
    dic = (res.json())["books"][0]
    rating_gd = dic['average_rating']
    count_gd = dic['work_ratings_count']
    if not db.execute("SELECT * FROM gd WHERE isbn = :isbn", {"isbn": isbn}).fetchone():
        db.execute("INSERT INTO gd (rating_gd, count_gd, isbn) VALUES (:rating_gd, :count_gd, :isbn)",{"rating_gd": rating_gd, "count_gd": count_gd, "isbn": isbn})
        db.commit()
    return render_template("book.html", book=book, reviews=reviews, count_gd=count_gd, rating_gd=rating_gd, isbn=isbn)

@app.route("/api/<isbn>")
def api(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "MMaRO0RhU3TAVsf60kU9lw", "isbns": isbn})
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify(res.status_code, {"error": "No such ISBN number"}), 404
    title = db.execute("SELECT title FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    title = title[0][0]
    author = db.execute("SELECT author FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    author = author[0][0]
    year = db.execute("SELECT year FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    year = year[0][0]

    data = res.json()
    count_gd = data["books"][0]['work_ratings_count']
    rating_gd  = data["books"][0]['average_rating']
    return jsonify({
            "title":title,
            "author": author,
            "year": year,
            "isbn": isbn,
            "review_count": count_gd,
            "average_score": rating_gd
            })
