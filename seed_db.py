import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()


books = [
    ("1984", "George Orwell", 1949, "Dystopia", "static/uploads/default.jpg", "https://example.com/1984"),
    ("To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", "static/uploads/default.jpg", "https://example.com/mockingbird"),
    ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "Classic", "static/uploads/default.jpg", "https://example.com/gatsby")
]

cursor.executemany(
    "INSERT INTO books (title, author, year, category, image_path, link) VALUES (?, ?, ?, ?, ?, ?)",
    books
)

conn.commit()
conn.close()

print("✅ Books inserted successfully!")
