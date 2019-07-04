import requests
import json
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "MMaRO0RhU3TAVsf60kU9lw", "isbns": "9781632168146"})
a = res.json()
b = (a["books"])

print(b[0]['isbn'])
