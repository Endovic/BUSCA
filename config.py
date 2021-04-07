"""App configurations
https://flask.palletsprojects.com/en/1.1.x/config/
"""

import os
from tempfile import mkdtemp

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    # https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options
    # SESSION_COOKIE_SECURE = True  # limits cookies to HTTPS traffic only
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True

class Production(Config):
    pass

class Development(Config):
    DEBUG = True

    # Configure server-side Sessions
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
