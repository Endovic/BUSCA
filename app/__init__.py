from flask import Flask
from flask_wtf.csrf import CSRFProtect   # https://flask-wtf.readthedocs.io/en/stable/csrf.html
import os   # for generating random byte sequence (for secret key) 

app = Flask(__name__)

# Configure Secret Key
SK = os.urandom(32) # see answer by Ahmed Ramzi. https://stackoverflow.com/questions/47687307/how-do-you-solve-the-error-keyerror-a-secret-key-is-required-to-use-csrf-whe
app.secret_key = SK

# Enable CSRF protection
csrf = CSRFProtect(app) # https://dev.to/dev0928/how-to-enable-csrf-protection-in-the-python-flask-app-5age

from app import views
from app import admin_views
from app import dbconnect
