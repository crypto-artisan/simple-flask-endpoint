from flask import Flask
app = Flask(__name__)

host = "127.0.0.1"
port = 3000
debug = False

@app.route('/')
def hello_world():
   return 'Hello World'

if __name__ == '__main__':
   app.run(host, port, debug)
