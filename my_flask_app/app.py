from flask import Flask, session

# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key_here"

# Import your routes
from routes import *

if __name__ == "__main__":
    app.run(debug=True)
