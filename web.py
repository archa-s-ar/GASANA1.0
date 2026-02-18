import os
import sqlite3
import json
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("pyq.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pyqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        scheme TEXT NOT NULL,
        semester INTEGER NOT NULL,
        subject TEXT NOT NULL,
        file_path TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()


HF_API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

def query(user_message):
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a calm and supportive academic companion. Validate feelings first, then give practical advice. Keep it under 120 words."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 200
        }
    )

    try:
        return response.json()
    except:
        return {"error": response.text}
    

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/learn_more")
def learn_more():
    return render_template("learn_more.html")


@app.route("/pyq", methods=["GET", "POST"])
def pyq():
    pdf_path = None

    conn = sqlite3.connect("pyq.db")
    cursor = conn.cursor()

    if request.method == "POST":
        dept = request.form.get("department")
        scheme = request.form.get("scheme")
        semester = request.form.get("semester")
        subject = request.form.get("subject")

        cursor.execute("""
        SELECT file_path FROM pyqs
        WHERE department=? AND scheme=? AND semester=? AND subject=?
        """, (dept, scheme, semester, subject))

        result = cursor.fetchone()
        if result:
            pdf_path = result[0]

    conn.close()

    return render_template("pyq.html", pdf_path=pdf_path)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/imp')
def imp():
    return render_template('imp.html')

@app.route('/xam_simu')
def xam_simu(): 
    return render_template('xam_simu.html')

@app.route('/doubt')
def doubt():
    return render_template('doubt.html')

@app.route("/stress", methods=["GET", "POST"])
def stress():
    reply = None

    if request.method == "POST":
        user_message = request.form.get("message")

        prompt = f"""
You are a calm and supportive academic companion.
The student says: "{user_message}"

Validate their feelings first.
Then give practical advice.
Keep response under 120 words.
Use short paragraphs.
"""

        output = query(user_message)
        

        if "choices" in output:
            reply = output["choices"][0]["message"]["content"]
        else:
            reply = output.get("error", "Something went wrong.")

    return render_template("stress.html", reply=reply)


if __name__ == "__main__":
    app.run(debug=True)