from flask import Flask, send_from_directory, request, jsonify, session, redirect
import sqlite3
import os
import html

app = Flask(__name__)

# Secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)

# Admin password from environment variable
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Database path
DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.root_path, "portfolio.db")
)


# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_table()


# Home page
@app.route("/")
def home():
    return send_from_directory(app.root_path, "index.html")


# CSS
@app.route("/style.css")
def css():
    return send_from_directory(app.root_path, "style.css")


# JavaScript
@app.route("/script.js")
def js():
    return send_from_directory(app.root_path, "script.js")


# Contact form backend
@app.route("/contact", methods=["POST"])
def contact():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({
            "message": "All fields are required!"
        }), 400

    conn = get_db_connection()

    conn.execute(
        "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Message saved successfully!"
    })


# Admin login
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password", "")

        if not ADMIN_PASSWORD:
            return "Admin password is not configured.", 503

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/dashboard")

        return """
        <h3>Incorrect password!</h3>
        <a href="/admin">Try again</a>
        """

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f0ff;
                text-align: center;
                padding: 100px;
            }

            form {
                background: white;
                padding: 30px;
                display: inline-block;
                border-radius: 12px;
            }

            input, button {
                padding: 12px;
                margin: 10px;
            }

            button {
                background: #8e44ad;
                color: white;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <form method="POST">
            <h2>Admin Login</h2>

            <input type="password"
                   name="password"
                   placeholder="Enter Admin Password"
                   required>

            <br>

            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """


# Admin dashboard
@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = get_db_connection()

    contacts = conn.execute(
        "SELECT * FROM contacts ORDER BY id DESC"
    ).fetchall()

    conn.close()

    rows = ""

    for contact in contacts:

        name = html.escape(contact["name"])
        email = html.escape(contact["email"])
        message = html.escape(contact["message"])

        rows += f"""
        <tr>
            <td>{contact['id']}</td>
            <td>{name}</td>
            <td>{email}</td>
            <td>{message}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>

        <style>
            body {{
                font-family: Arial;
                background: #f5f0ff;
                padding: 30px;
            }}

            h1 {{
                color: #6c3483;
                text-align: center;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                margin-top: 25px;
            }}

            th, td {{
                padding: 15px;
                border: 1px solid #ddd;
                text-align: left;
                overflow-wrap: anywhere;
            }}

            th {{
                background: #8e44ad;
                color: white;
            }}
        </style>
    </head>

    <body>

        <h1>Portfolio Admin Dashboard</h1>

        <h2>Contact Messages</h2>

        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Message</th>
            </tr>

            {rows}

        </table>

        <br>

        <a href="/logout">Logout</a>

    </body>
    </html>
    """


# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/admin")


# Run Flask application
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )