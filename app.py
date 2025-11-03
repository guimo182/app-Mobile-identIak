#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "identikai.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# ---------- Database helpers ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Auth utilities ----------
def current_user():
    uid = session.get("user_id")
    if not uid: 
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return user

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template('index.html', user=current_user())

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            nxt = request.args.get('next') or url_for('face_register')
            return redirect(nxt)
        flash("Credenciales inválidas", "error")
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not email or not password:
            flash("Debes ingresar correo y contraseña", "error")
            return render_template('signup.html')
        try:
            conn = get_db()
            conn.execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",
                         (email, generate_password_hash(password), datetime.utcnow().isoformat()))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            conn.close()
            session['user_id'] = user['id']
            return redirect(url_for('face_register'))
        except sqlite3.IntegrityError:
            flash("Ese correo ya está registrado.", "error")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/face')
@login_required
def face_register():
    return render_template('face.html', user=current_user())

@app.post('/api/verify')
@login_required
def api_verify():
    """
    Demo endpoint: receives a base64 image from the browser, stores it,
    and records an attendance entry. Returns success JSON.
    No ML is performed in this mock.
    """
    import base64
    data_url = request.json.get("image")
    if not data_url or not data_url.startswith("data:image/"):
        return jsonify({"ok": False, "error": "Imagen inválida"}), 400

    header, b64data = data_url.split(",", 1)
    ext = header.split(";")[0].split("/")[1]
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user()['id']}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64data))

    conn = get_db()
    conn.execute("INSERT INTO attendance(user_id,image_path,created_at) VALUES(?,?,?)",
                 (current_user()['id'], filename, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "redirect": url_for('success')})

@app.route('/success')
@login_required
def success():
    return render_template('success.html', user=current_user())

# Static download of captured images (dev only)
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
