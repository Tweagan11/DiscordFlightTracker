from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
import os
import amadeus

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Discord Flight Tracker!"

@app.route('/api-status')
def get_status():
    amadeus.get_api_token()
                             


if __name__ == '__main__':
    PORT = int(os.getenv("PORT", 5000))
    app.run(port=PORT)
    