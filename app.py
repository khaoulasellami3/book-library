import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3

UPLOAD_FOLDER = "static/uploads"  
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = "secret123"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)  
    per_page = 8
    offset = (page - 1) * per_page
    search = request.args.get("search", "") 

    conn = get_db_connection()

    if search:
        books = conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? LIMIT ? OFFSET ?",
            (f"%{search}%", f"%{search}%", per_page, offset)
        ).fetchall()
        total_books = conn.execute(
            "SELECT COUNT(*) FROM books WHERE title LIKE ? OR author LIKE ?",
            (f"%{search}%", f"%{search}%")
        ).fetchone()[0]
    else:
        books = conn.execute("SELECT * FROM books LIMIT ? OFFSET ?", (per_page, offset)).fetchall()
        total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    conn.close()

    total_pages = (total_books + per_page - 1) // per_page

    return render_template("index.html", books=books, page=page, total_pages=total_pages, search=search)


@app.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"]
        category = request.form["category"]
        link = request.form["link"]

        image = request.files.get("image")  
        image_path = None

        if image and image.filename != "" and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            image_path = image_path.replace("\\", "/")
        else:
            # Default image
            image_path = "static/uploads/default.jpg"

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO books (title, author, year, category, image_path, link) VALUES (?, ?, ?, ?, ?, ?)",
            (title, author, year, category, image_path, link)
        )
        conn.commit()
        conn.close()

        flash("✅ Book added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")

# update
@app.route("/update/<int:id>", methods=("GET", "POST"))
def update(id):
    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"]
        category = request.form["category"]
        link = request.form["link"]

       
        image = request.files.get("image")
        image_path = book["image_path"] 
        if image and image.filename != "" and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            image_path = image_path.replace("\\", "/")

        conn.execute(
            "UPDATE books SET title=?, author=?, year=?, category=?, image_path=?, link=? WHERE id=?",
            (title, author, year, category, image_path, link, id)
        )
        conn.commit()
        conn.close()

        flash("✏️ Book updated!", "info")
        return redirect(url_for("index"))

    conn.close()
    return render_template("update.html", book=book)


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
