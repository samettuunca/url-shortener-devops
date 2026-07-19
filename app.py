from flask import Flask, request, redirect, jsonify
import random
import string
import sqlite3

app = Flask(__name__)

DB_PATH = "/app/data/urls.db"

def veritabani_baslat():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            kod TEXT PRIMARY KEY,
            long_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

veritabani_baslat()

def kod_var_mi(kod):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM urls WHERE kod = ?", (kod,))
    sonuc = cursor.fetchone()
    conn.close()
    return sonuc is not None

def kisa_kod_uret():
    karakterler = string.ascii_letters + string.digits
    kod = ''.join(random.choices(karakterler, k=6))
    while kod_var_mi(kod):
        kod = ''.join(random.choices(karakterler, k=6))
    return kod

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    long_url = data.get("url")

    if not long_url:
        return jsonify({"hata": "url alanı gerekli"}), 400

    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        return jsonify({"hata": "geçerli bir URL girin (http:// veya https:// ile başlamalı)"}), 400

    kod = kisa_kod_uret()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (kod, long_url) VALUES (?, ?)", (kod, long_url))
    conn.commit()
    conn.close()

    return jsonify({"kisa_link": f"http://127.0.0.1:5000/{kod}"}), 201

@app.route("/<kod>")
def yonlendir(kod):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE kod = ?", (kod,))
    sonuc = cursor.fetchone()
    conn.close()

    if not sonuc:
        return jsonify({"hata": "kod bulunamadı"}), 404

    return redirect(sonuc[0])

if __name__ == "__main__":
    app.run(debug=True)