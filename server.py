import flask as Flask

app = Flask.Flask(__name__)

@app.route('/')
def home():
    return "Hello, Discord Flight Tracker!"



if __name__ == '__main__':
    PORT = 5000
    app.run(port=PORT)