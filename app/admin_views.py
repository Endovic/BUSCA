from app import app

from flask import render_template, redirect, request, url_for, session
from flask_session import Session
from tempfile import mkdtemp    # see Finance CS50
from functools import wraps
from werkzeug.security import check_password_hash
import re
from collections import defaultdict

from .dbconnect import query_db, get_db

# Ensure responses aren't cached (in debugging mode)
# https://pythonise.com/series/learning-flask/python-before-after-request
# https://devcenter.heroku.com/articles/increasing-application-performance-with-http-cache-headers
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure Sessions
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# app.config["SESSION_COOKIE_SECURE"] = True  # limits cookies to HTTPS traffic only
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
# https://flask.palletsprojects.com/en/1.1.x/security/
# https://flask-session.readthedocs.io/en/latest/
Session(app)


# Implement login required Decorator
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# (helper function) Log admin changes
def logChanges(ch, et, nm, ad):

    # Get UTC date/time of change using SQLite function: https://www.sqlitetutorial.net/sqlite-date/
    date = query_db("SELECT datetime('now')")[0]["datetime('now')"]

    query_db("""INSERT INTO changes (change, entry, name, admin_id, date)       
        VALUES (?, ?, ?, ?, ?)""", (ch, et, nm, ad, date))
    return

# Application views

@app.route("/admin/")
def gotodashboard():
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("/admin/login.html")
    
    elif request.method == "POST":

        # Query database for nickname
        row = query_db("SELECT * FROM admin WHERE nicknm = ?", [request.form.get("nickname")])

        # Ensure username exists and password is correct
        if row and check_password_hash(row[0]["passwd"], request.form.get("password")):

            # Remember which user has logged in
            session["user_id"] = row[0]["id"]  # access value by column name https://www.kite.com/python/docs/sqlite3.Row
                        
            return redirect(url_for("admin_dashboard"))

        else:
            return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route("/admin/new", methods=["GET", "POST"])
@login_required
def admin_new():  
    """Add new record to database"""

    # User reached route via link from dashboard -> present empty form
    if request.method == "GET":
        concelhos = query_db("SELECT municipio FROM territory ORDER BY municipio COLLATE noaccents")
        tipos = [
            ("CRO", "CRO"),
            ("Associação de Proteção Animal", "ASFL - Associação"),
            ("Particular", "ASFL - Particular"),
            ("Hospital", "CAMV - Hospital"),
            ("Clínica", "CAMV - Clínica"),
            ("Consultório", "CAMV - Consultório")
        ]
        return render_template("admin/new.html", conc=concelhos, tipos=tipos)
    
    # User submitted a new record -> save in database
    elif request.method == "POST":
        name = request.form.get("nome").upper()
        location = request.form.get("concelho")
        subtype = request.form.get("tipo")
        maintype = query_db("SELECT tipo FROM contacts WHERE subtipo = ?", [subtype])[0]["tipo"]
        # Save empty facultative fields as NULL in the database:
        tel1 = (request.form.get("tel-1") if request.form.get("tel-1") != '' else None) # https://www.pythoncentral.io/one-line-if-statement-in-python-ternary-conditional-operator/
        tel2 = (request.form.get("tel-2") if request.form.get("tel-2") != '' else None)
        tel3 = (request.form.get("tel-3") if request.form.get("tel-3") != '' else None)
        tel4 = (request.form.get("tel-4") if request.form.get("tel-4") != '' else None)
        email1 = (request.form.get("email-1") if request.form.get("email-1") != '' else None)
        email2 = (request.form.get("email-2") if request.form.get("email-2") != '' else None)
        email3 = (request.form.get("email-3") if request.form.get("email-3") != '' else None)
        morada1a = (request.form.get("morada-1a") if request.form.get("morada-1a") != '' else None)
        morada1b = (request.form.get("morada-1b") if request.form.get("morada-1b") != '' else None)
        cp1 = (request.form.get("cpostal-1") if request.form.get("cpostal-1") != '' else None)
        lugar1 = (request.form.get("lugar-1") if request.form.get("lugar-1") != '' else None)
        morada2a = (request.form.get("morada-2a") if request.form.get("morada-2a") != '' else None)
        morada2b = (request.form.get("morada-2b") if request.form.get("morada-2b") != '' else None)
        cp2 = (request.form.get("cpostal-2") if request.form.get("cpostal-2") != '' else None)
        lugar2 = (request.form.get("lugar-2") if request.form.get("lugar-2") != '' else None)
        web1 = (request.form.get("website-1") if request.form.get("website-1") != '' else None)
        web2 = (request.form.get("website-2") if request.form.get("website-2") != '' else None)
        extra = (request.form.get("extra-info") if request.form.get("extra-info") != '' else None)

        actualizado = query_db("SELECT date('now')")[0]["date('now')"]

        try:
            query_db("""INSERT INTO contacts
                (nome, tipo, subtipo, tel_1, tel_2, tel_3, tel_4, email_1, email_2, email_3, morada_1a, morada_1b, cpostal_1, lugar_1, morada_2a, morada_2b, cpostal_2, lugar_2, website_1, website_2, extra_info, actualizado)       
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, maintype, subtype, tel1, tel2, tel3, tel4, email1, email2, email3, morada1a, morada1b, cp1, lugar1, morada2a, morada2b, cp2, lugar2, web1, web2, extra, actualizado))

            newcode = query_db("SELECT code FROM territory WHERE municipio = ?", [location])[0]["code"]
            newid = query_db("SELECT id FROM contacts WHERE nome = ?", [name])[0]["id"]
            query_db("INSERT INTO places (code, id) VALUES (?, ?)", (newcode, newid))
            
            logChanges("new", newid, name, session.get("user_id"))
            get_db().commit()
        except:
        # UNIQUE constraint failed - a record with the same name already exists in the database
            return redirect(url_for('admin_new'))

        return redirect(url_for("admin_dashboard"))

@app.route("/admin/update", methods=["GET", "POST"])
@login_required
def admin_update():
    """Update or delete record from database"""

    # Helper functions to reuse in POST requests

    def search(name):
        # Escape special characters to avoid FTS5 syntax error
        name = re.sub(r"[+_'\/-]", ' ', name)
        name = re.sub(r"[^\w\s]", '', name)
        # Query database
        results = query_db("""SELECT id, code, nome, tipo, municipio FROM places
            JOIN (SELECT * FROM contacts_fts WHERE contacts_fts MATCH ? ORDER BY rank) USING (id)
            JOIN territory USING (code)""", [name])
        return results
    
    def search_all():
        # Get all records from database
        results = query_db("""SELECT id, code, nome, tipo, municipio FROM places
                JOIN contacts USING (id)
                JOIN territory USING (code)
                ORDER BY nome COLLATE noaccents""")
        return results
    
    # User performed a name search -> present list of results
    # or selected a record to delete -> delete record from database
    if request.method == "POST":

        # Search records
        if request.form["action"] == "search":            
            name = request.form.get("name")
            if not name:
                results = search_all()
                return render_template("admin/update.html", results=results, count=len(results))
        
            if not re.findall(r"[^\W_]", name):
                return redirect(url_for("admin_update"))

            results = search(name)
            return render_template("admin/update.html", results=results, count=len(results), input=name)
        
        # Delete record
        elif request.form["action"] == "delete":
            entry_id = request.form.get("entry-id")
            entry_code = request.form.get("entry-code")
            
            query_db("DELETE FROM contacts WHERE id = ?", [entry_id])
            query_db("DELETE FROM places WHERE id = ? AND code = ?", (entry_id, entry_code))
            
            logChanges("del", entry_id, request.form.get("entry-name"), session.get("user_id"))
            get_db().commit()
            
            name = request.form.get("name")
            if not name:
                results = search_all()
                return render_template("admin/update.html", results=results, count=len(results))

            results = search(name)
            return render_template("admin/update.html", results=results, count=len(results), input=name)
        
    # User reached route via link from dashboard -> present a search bar
    elif request.method == "GET":
        return render_template("admin/update.html")

@app.route("/admin/update/<record>", methods=["GET", "POST"])
@login_required
def admin_modify(record):
    """Make changes to record in database"""

    # User selected a record to update -> present a form filled with the record data
    if request.method == "GET":
        record_data = query_db("""SELECT * FROM places
            JOIN contacts USING (id)
            JOIN territory USING (code)
            WHERE id = ?""", [record])

        # Assign the empty string to NULL/None items (so that the placeholder is rendered instead of the <option> value)
        record = defaultdict()  # https://www.accelebrate.com/blog/using-defaultdict-python
        for key in record_data[0].keys():   # https://www.kite.com/python/docs/sqlite3.Row
            item = record_data[0][key]
            record[key] = (item if item else '')
            
        concelhos = query_db("SELECT municipio FROM territory ORDER BY municipio COLLATE noaccents")
        tipos = [
            ("CRO", "CRO"),
            ("Associação de Proteção Animal", "ASFL - Associação"),
            ("Particular", "ASFL - Particular"),
            ("Hospital", "CAMV - Hospital"),
            ("Clínica", "CAMV - Clínica"),
            ("Consultório", "CAMV - Consultório")
        ]

        return render_template("admin/update.html",
            record=record, input=request.args.get("name"), conc=concelhos, tipos=tipos)

    # User submitted changes to a record -> save in database
    elif request.method == "POST":
        name = request.form.get("nome").upper()
        location = request.form.get("concelho")
        subtype = request.form.get("tipo")
        maintype = query_db("SELECT tipo FROM contacts WHERE subtipo = ?", [subtype])[0]["tipo"]
        tel1 = (request.form.get("tel-1") if request.form.get("tel-1") != '' else None)
        tel2 = (request.form.get("tel-2") if request.form.get("tel-2") != '' else None)
        tel3 = (request.form.get("tel-3") if request.form.get("tel-3") != '' else None)
        tel4 = (request.form.get("tel-4") if request.form.get("tel-4") != '' else None)
        email1 = (request.form.get("email-1") if request.form.get("email-1") != '' else None)
        email2 = (request.form.get("email-2") if request.form.get("email-2") != '' else None)
        email3 = (request.form.get("email-3") if request.form.get("email-3") != '' else None)
        morada1a = (request.form.get("morada-1a") if request.form.get("morada-1a") != '' else None)
        morada1b = (request.form.get("morada-1b") if request.form.get("morada-1b") != '' else None)
        cp1 = (request.form.get("cpostal-1") if request.form.get("cpostal-1") != '' else None)
        lugar1 = (request.form.get("lugar-1") if request.form.get("lugar-1") != '' else None)
        morada2a = (request.form.get("morada-2a") if request.form.get("morada-2a") != '' else None)
        morada2b = (request.form.get("morada-2b") if request.form.get("morada-2b") != '' else None)
        cp2 = (request.form.get("cpostal-2") if request.form.get("cpostal-2") != '' else None)
        lugar2 = (request.form.get("lugar-2") if request.form.get("lugar-2") != '' else None)
        web1 = (request.form.get("website-1") if request.form.get("website-1") != '' else None)
        web2 = (request.form.get("website-2") if request.form.get("website-2") != '' else None)
        extra = (request.form.get("extra-info") if request.form.get("extra-info") != '' else None)

        actualizado = query_db("SELECT date('now')")[0]["date('now')"]

        target_id = request.form.get("id")

        try:
            query_db("""UPDATE contacts
                SET nome = ?, tipo = ?, subtipo = ?, tel_1 = ?, tel_2 = ?, tel_3 = ?, tel_4 = ?, email_1 = ?, email_2 = ?,
                email_3 = ?, morada_1a = ?, morada_1b = ?, cpostal_1 = ?, lugar_1 = ?, morada_2a = ?, morada_2b = ?,
                cpostal_2 = ?, lugar_2 = ?, website_1 = ?, website_2 = ?, extra_info = ?, actualizado = ?
                WHERE id = ?""",   
                (name, maintype, subtype, tel1, tel2, tel3, tel4, email1, email2, email3, morada1a, morada1b, cp1, lugar1, morada2a, morada2b, cp2, lugar2, web1, web2, extra, actualizado, target_id))
        
            newcode = query_db("SELECT code FROM territory WHERE municipio = ?", [location])[0]["code"]
            query_db("UPDATE places SET code = ? WHERE id = ?", (newcode, target_id))
            
            logChanges("mod", target_id, name, session.get("user_id"))
            get_db().commit()
        
        except:
        # UNIQUE constraint failed - a record with the same name already exists in the database
        # (redirect passing along data) https://sodocumentation.net/flask/topic/6856/redirect
            return redirect(url_for('admin_modify', record=record))

        return redirect(url_for("admin_dashboard"))

@app.route("/admin/list")
@login_required
def admin_list():
    """Show full list of records in database"""

    records = query_db("""SELECT * FROM places
                    JOIN contacts USING (id)
                    JOIN territory USING (code)
                    ORDER BY nome COLLATE noaccents""")
    return render_template("admin/list.html", records=records, count=len(records))
