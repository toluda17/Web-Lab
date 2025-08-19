from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for sessions

# Database helper
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        # Intentionally vulnerable SQL injection
        user = conn.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'").fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()

    return render_template("profile.html", user=user)

def init_db():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # project root
    schema_path = os.path.join(base_dir, "db", "schema.sql")

    conn = sqlite3.connect(os.path.join(base_dir, "database.db"))
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/search")
def search():
    return "TODO: implement search functionality"

@app.route("/upload", methods=["GET", "POST"])
def upload():
    return "TODO: implement file upload functionality"

if __name__ == "__main__":
    app.run(debug=True)
