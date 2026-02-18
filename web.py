import os
import sqlite3
import PyPDF2
import requests
from flask import Flask, render_template, request, redirect, url_for

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

def query(user_message, system_role=None):

    if not system_role:
        system_role = "You are a helpful assistant."

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 300
        }
    )

    return response.json()
    

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

@app.route('/xam_simu', methods=["GET", "POST"])
def xam_simu():
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

    return render_template("xam_simu.html", pdf_path=pdf_path)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("answer_pdf")

    if not file:
        return "No file uploaded"

    if file.filename.endswith(".pdf"):

        os.makedirs("uploads", exist_ok=True)
        save_path = os.path.join("uploads", file.filename)
        file.save(save_path)

        # Extract text from PDF
        text = ""
        with open(save_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""

        # Send to AI for evaluation
        evaluation_prompt = f"""
You are an exam evaluator.

Evaluate the following student answer sheet.

Give:
1. Estimated score out of 100
2. Strengths (bullet points)
3. Areas of improvement (bullet points)

Keep response structured and under 150 words.

Answer Sheet:
{text}
"""

        output = query(evaluation_prompt)

        if "choices" in output:
            feedback = output["choices"][0]["message"]["content"]
        else:
            feedback = "Evaluation failed."

        return render_template("result.html", feedback=feedback)

    return "Only PDF files allowed."


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