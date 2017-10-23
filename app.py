from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
# Connect to MySQL server
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
# Print SQL comms in terminal
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'asdfg67890tytyty'

# Create python database object
db = SQLAlchemy(app)

