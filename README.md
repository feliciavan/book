# Book Review

It's a book review website. Users can signup and login. It has a lot of book information and users can search any book they want. Using a third-party API by Goodreads, book information and review rates can be shown. Users from this website can also give some comments.

application.py is the FLASK_APP.
books.csv is the source of books in SQL.
goodread.py is the test code for API provided by project 1.
import.py is the code for importing book data in books.csv to Adminer data server.
reviews.sql and users_gd.sql are both SQL commands.

In templates:
book.html is the book page which presents details and reviews of the book and through which you can make your own review and rating. And rating is a nessary input while review is not.
error.html is alert pages.
index.html is the homepage which contains login and signup funcitons.
json.html is about json which is required by project 1.
layout.html is about layout.
list.html is the list of search results.
search.html is only for searching.
signup.html is sing up page which only needs user name and password.
