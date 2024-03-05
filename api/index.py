from flask import Flask, render_template

app = Flask(__name__)
host = "127.0.0.1"
port = 3000
debug = False
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return 'About'