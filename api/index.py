from flask import Flask

app = Flask(__name__)
host = "127.0.0.1"
port = 3000
debug = False
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'