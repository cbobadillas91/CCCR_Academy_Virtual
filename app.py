from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_cccr'

# --------------------------
# Crear base de datos
# --------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# --------------------------
# Página principal (PROTEGIDA)
# --------------------------
@app.route("/")
def inicio():
    if 'user' in session:
        return render_template("index.html")
    else:
        return redirect("/login")

# --------------------------
# Página de curso (PROTEGIDA)
# --------------------------
@app.route("/curso")
def curso():
    if 'user' in session:
        return render_template("curso.html")
    else:
        return redirect("/login")

# --------------------------
# LOGIN
# --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "Correo o contraseña incorrectos"

    return render_template("login.html")

# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# --------------------------
# Ejecutar servidor
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)