from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import sqlite3
import os
import werkzeug.utils
from markupsafe import escape 
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for sessions
DB_PATH = "database.db"  # Single database file
SECURE_MODE = False  # Change to True for secure mode

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database helper
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database if it doesn't exist
def init_db():
    """Initialize the database only if the users table doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if 'users' table exists
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='users';
    """)
    table_exists = cursor.fetchone()

    if not table_exists:
        # Only create table if it doesn't exist
        schema_path = os.path.join(os.path.dirname(__file__), "db", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                conn.executescript(f.read())
            print("Database initialized from schema.sql")
        else:
            # Fallback: create users table directly
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            print("Database initialized with default users table")
        conn.commit()
    else:
        print("Users table already exists, skipping initialization")

    conn.close()

class ChangePasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    submit = SubmitField("Change")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None  # To store any error message

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()  # <- use the same helper as other routes
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", 
                (username, password)
            )
            conn.commit()
            return "Registration successful!"
        except sqlite3.IntegrityError:
            error = "Username already exists. Please choose another."
        finally:
            conn.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        if SECURE_MODE:
            # ✅ Secure: parameterized query
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
        else:
            # ❌ Vulnerable: raw string concatenation (SQLi possible!)
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            print("DEBUG (insecure query):", query)  # Optional, to see it in logs
            user = conn.execute(query).fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            return "Invalid credentials"

    return render_template("login.html")



@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

    if request.method == "POST":
        bio = request.form["bio"]

        if SECURE_MODE:
            # ✅ Secure: escape user input before saving
            bio_to_save = escape(bio)
        else:
            # ❌ Vulnerable: save raw user input (XSS possible!)
            bio_to_save = bio

        conn.execute("UPDATE users SET bio=? WHERE id=?", (bio_to_save, user["id"]))
        conn.commit()

        # Refresh user after update
        user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

    conn.close()
    return render_template("profile.html", user=user)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if SECURE_MODE:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            new_password = form.password.data
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session["user_id"]))
                conn.commit()
            return "Password changed successfully (secure)!"
        return render_template_string("""
            <form method="POST">
                {{ form.hidden_tag() }}
                {{ form.password.label }} {{ form.password() }}<br>
                {{ form.submit() }}
            </form>
        """, form=form)
    else:
        # ❌ Vulnerable path: no CSRF token required
        if request.method == "POST":
            new_password = request.form.get("password", "")
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session["user_id"]))
                conn.commit()
            return "Password changed (insecure, no CSRF)!"
        return """
            <form method="POST">
                <label>New Password:</label>
                <input type="password" name="password" />
                <button type="submit">Change</button>
            </form>
        """

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file:
            filename = werkzeug.utils.secure_filename(uploaded_file.filename)

            if SECURE_MODE:
                # ✅ Secure: only allow certain file types
                allowed_exts = ["txt", "jpg", "png", "pdf", "jpeg"]
                if filename.split(".")[-1].lower() not in allowed_exts:
                    message = "File type not allowed!"
                else:
                    uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))
                    message = f"File safely uploaded as {filename}"
            else:
                # ❌ Vulnerable: accept anything
                uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))
                message = f"File uploaded to {UPLOAD_FOLDER}\\{filename}"

    # Simple upload form
    return f"""
        <h2>Upload a file</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
        <p>{message}</p>
    """

# Route to serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/search")
def search():
    return "TODO: implement search functionality"

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

