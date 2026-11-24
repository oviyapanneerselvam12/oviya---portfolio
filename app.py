from flask import Flask, send_from_directory, request, jsonify, session, redirect
import sqlite3
import os

app = Flask(__name__)

# Secret key for session
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

# Admin login password
ADMIN_PASSWORD = "admin123"


# Database connection
def get_db_connection():
    conn = sqlite3.connect("portfolio.db")
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
    return send_from_directory(".", "index.html")


# CSS file
@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")


# JavaScript file
@app.route("/script.js")
def js():
    return send_from_directory(".", "script.js")


# Contact form backend
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"message": "All fields are required!"}), 400

    conn = get_db_connection()

    conn.execute(
        "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Message saved successfully!"})


# Admin login page
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")

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
            <input type="password" name="password"
                   placeholder="Enter Admin Password" required>
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
        rows += f"""
        <tr>
            <td>{contact['id']}</td>
            <td>{contact['name']}</td>
            <td>{contact['email']}</td>
            <td>{contact['message']}</td>
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
            a {{
                color: #8e44ad;
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


# Admin logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)