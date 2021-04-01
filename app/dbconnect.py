"""
Configure connection and functions to interact with database.
(can be imported to app views via syntax: from .dbconnect import fx1, fx2, etc.)
(example: https://github.com/pallets/flask/blob/master/src/flask/helpers.py)
"""

from app import app

import psycopg2 # https://devcenter.heroku.com/articles/heroku-postgresql#connecting-in-python
from psycopg2.extras import DictCursor # https://www.psycopg.org/docs/extras.html
from flask import g

# Configure database
DATABASE = {
    "host": "localhost",
    "port": "5432",
    "name": "busca",
    "user": "postgres",
    "pw": "revigres"
}

# Open database connection on demand
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = psycopg2.connect(
            host=DATABASE["host"],
            port=DATABASE["port"],
            dbname=DATABASE["name"],
            user=DATABASE["user"],
            password=DATABASE["pw"]
        )    
    return db

# Query function that combines getting the cursor, executing and fetching the results
def query_db(query, args=(), one=False):
    cur = get_db().cursor(cursor_factory=DictCursor)    # dict cursor for easy querying
    cur.execute(query, args)
    try:
        rv = cur.fetchall()
    except:
        rv = None
    finally:
        cur.close()
        return (rv[0] if rv else None) if one else rv

# Close database connection when context dies (at the end of the request)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db. close()
