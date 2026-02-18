from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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

@app.route('/stress')
def stress():
    return render_template('stress.html')


if __name__ == "__main__":
    app.run(debug=True)