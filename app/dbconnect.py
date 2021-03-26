"""
Configure connection and functions to interact with database.
(can be imported to app views via syntax: from .dbconnect import fx1, fx2, etc.)
(example: https://github.com/pallets/flask/blob/master/src/flask/helpers.py)
"""

from app import app

import sqlite3  # https://docs.python.org/3/library/sqlite3.html
from flask import g
from unidecode import unidecode # https://pypi.org/project/Unidecode/

# Configure SQLite3 database connection. https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
DATABASE = "database/busca.db"

# Collation algorithm for converting unicode chars (accented) into ASCII characters when sorting from database
# https://wellsr.com/python/making-new-collations-with-python-sqlite-create_collation/
def collate_noaccents(name1, name2):
    n1 = unidecode(name1)
    n2 = unidecode(name2)
    return 1 if n1.lower() > n2.lower() else -1 if n1.lower() < n2.lower() else 0

def get_db():
    # Open database connection on demand
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    
    # Create row factory for easy querying https://www.kite.com/python/docs/sqlite3.Row
    db.row_factory = sqlite3.Row

    # Create collation for accent-insensitive sorting
    db.create_collation("noaccents", collate_noaccents)

    return db

# Query function that combines getting the cursor, executing and fetching the results
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Close database connection when context dies (at the end of the request)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db. close()
