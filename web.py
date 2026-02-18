import os
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


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

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # TODO: Check database here

        return redirect('/dashboard')

    return render_template('login.html')

# CREATE ACCOUNT
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Save to database later

        return redirect('/login')

    return render_template('createac.html')


@app.route('/pyq')
def pyq():
    return render_template('pyq.html')

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