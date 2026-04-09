from flask import Flask, render_template, request, redirect, session
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_cccr'

# --------------------------
# VALIDAR CONTRASEÑA
# --------------------------
def validar_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# --------------------------
# Crear / actualizar base de datos
# --------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            role TEXT
        )
    ''')

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    except:
        pass

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
# LOGIN (🔥 SOLO SE ARREGLA CON ROW_FACTORY)
# --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row   # 🔥 AGREGADO (CLAVE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["email"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect("/")
        else:
            return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")

# --------------------------
# REGISTRO
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if not validar_password(password):
            return "La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo"

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, "user")
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# --------------------------
# CREAR USUARIO (solo admin)
# --------------------------
@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if not validar_password(password):
            return render_template("crear_usuario.html", error="La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo")

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existe = cursor.fetchone()

        if existe:
            conn.close()
            return render_template("crear_usuario.html", error="Ese correo ya existe")

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role)
        )

        conn.commit()
        conn.close()

        return render_template("crear_usuario.html", exito="Usuario creado correctamente")

    return render_template("crear_usuario.html")

# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    session.pop("name", None)
    return redirect("/login")

# --------------------------
# ADMIN (solo admin)
# --------------------------
@app.route("/admin")
def admin():
    if "user" in session and session.get("role") == "admin":
        return "Panel de administrador"
    else:
        return redirect("/")

# --------------------------
# Ejecutar servidor
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)