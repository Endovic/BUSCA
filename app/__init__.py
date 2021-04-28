from flask import Flask
from flask_wtf.csrf import CSRFProtect  # https://flask-wtf.readthedocs.io/en/stable/csrf.html
from flask_session import Session   # https://flask-session.readthedocs.io/en/latest/
import dotenv   # https://flask.palletsprojects.com/en/1.1.x/cli/#environment-variables-from-dotenv

app = Flask(__name__)

# Load app configurations
# https://pythonise.com/series/learning-flask/flask-configuration-files
if app.env == "development":
    """DEVELOPMENT (DEBUGGING) MODE"""
    app.config.from_object("config.Development")

    # Activate server-side session configuration
    Session(app)

    # Prevent cached responses
    # https://pythonise.com/series/learning-flask/python-before-after-request
    # https://devcenter.heroku.com/articles/increasing-application-performance-with-http-cache-headers
    # https://www.freecodecamp.org/news/an-in-depth-introduction-to-http-caching-cache-control-vary/
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response
else:
    """PRODUCTION MODE"""
    app.config.from_object("config.Production")

    # Prevent cached responses for dynamically generated content but cache static files (see duration in config)
    # https://subscription.packtpub.com/book/web_development/9781782169628/1/ch01lvl1sec12/handling-static-files-simple
    @app.after_request
    def after_request(response):
        if "Cache-Control" not in response.headers: # https://stackoverflow.com/questions/23112316/using-flask-how-do-i-modify-the-cache-control-header-for-all-output/37331139
            response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
        return response

# Enable CSRF protection
# https://dev.to/dev0928/how-to-enable-csrf-protection-in-the-python-flask-app-5age
csrf = CSRFProtect(app)

# Import all components of the app package
# https://pythonise.com/series/learning-flask/flask-application-structure
from app import views
from app import admin_views
from app import dbconnect
