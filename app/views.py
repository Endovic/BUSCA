from app import app

from flask import render_template, redirect, request, url_for, session, jsonify, json, flash
from collections import defaultdict # https://stackabuse.com/introduction-to-pythons-collections-module/
import re   # regex
import sys  # for error handling (sys.exc_info()) https://www.kite.com/python/docs/sys.exc_info

from .dbconnect import query_db, get_db

# App public views:

@app.route("/")
def index():
    return redirect(url_for("homepage"))

@app.route("/animais-desaparecidos")
def homepage():
    return render_template("public/index.html")

@app.route("/acerca-do-projeto")
def about():
    return render_template("public/about.html")

@app.route("/privacidade")
def privacy():
    return render_template("public/privacy.html")

@app.route("/contacte-nos", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("public/contact.html")
    
    if request.method == "POST":
        subject = request.form.get("subject")
        message = request.form.get("message")
        guestname = request.form.get("guestname")
        guestmail = request.form.get("guestmail")

        # Save empty facultative fields as NULL in the database:
        guestname = (request.form.get("guestname") if request.form.get("guestname") != '' else None) # https://www.pythoncentral.io/one-line-if-statement-in-python-ternary-conditional-operator/
        guestmail = (request.form.get("guestmail") if request.form.get("guestmail") != '' else None)

        try:
            query_db("INSERT INTO messages (sub, msg, visitor, email) VALUES (%s, %s, %s, %s)",
                (subject, message, guestname, guestmail))
            # date/time of submission is recorded automatically in the database when INSERT takes place
            # https://www.postgresqltutorial.com/postgresql-current_timestamp/
            
            get_db().commit()
        except:
            print(sys.exc_info())   # https://www.kite.com/python/docs/sys.exc_info
            flash("Ocorreu um erro e a sua mensagem não foi registada. Por favor contacte-nos através do nosso endereço de e-mail enquanto corrigimos o erro. Obrigado.", "error")
            return redirect(url_for("contact"))

        flash("A sua mensagem foi registada com sucesso.")
        return redirect(url_for("contact"))

@app.route("/pesquisa-entidades", methods=["GET", "POST"])
def search():
    # Get locations from database
    distrilhas = query_db("SELECT DISTINCT distrilha FROM territory ORDER BY distrilha") # (DISTINCT removes duplicate rows)
    concelhos = query_db("SELECT municipio FROM territory ORDER BY municipio")

    # Get types of entities from database (convert returned dictionary of row objects into a list of strings)
    entidades = query_db("SELECT DISTINCT subtipo FROM contacts")
    lista_entidades = []
    for entidade in entidades:
        lista_entidades.append(entidade["subtipo"])
    
    if request.method == "GET":
        # Render search page with default filters
        return render_template("public/search.html", dist=distrilhas, conc=concelhos,
            select_dist="Todos", select_conc="Todos")

    elif request.method == "POST":

        # Name search
        # (distinguish forms via hidden input in HTML)
        # https://stackoverflow.com/questions/45124603/how-to-tell-which-html-form-was-submitted-to-flask
        if request.form["search-by"] == "name":
            name = request.form.get("name")
           
            # Ensure that text is submitted and contains alphanumeric characters
            if not name or not re.findall(r"[^\W_]", name): # (\W matches any char which is not alphanum. nor the underscore)
                flash("Insira o nome de uma entidade para pesquisar.", "error")
                return render_template("public/search.html", dist=distrilhas, conc=concelhos,
                    select_dist="Todos", select_conc="Todos")

            # Valid text was submitted - query the database and present results
            else:
                try:                    
                    # Full-text search. https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-PARSING-DOCUMENTS
                    # 'ptunaccent' configuration: portuguese dictionary and diacritic-insensitive search
                    # (this query gets each contact only once even if it's in more than one place)
                    results = query_db("""SELECT * FROM contacts
                        WHERE to_tsvector('ptunaccent', nome) @@ websearch_to_tsquery('ptunaccent', %s)
                        ORDER BY nome""", [name])
                except:
                    print(sys.exc_info())   # https://www.kite.com/python/docs/sys.exc_info
                    flash("Ocorreu um erro. Altere os termos de pesquisa e tente novamente.", "error")
                    return render_template("public/search.html", dist=distrilhas, conc=concelhos,
                        select_dist="Todos", select_conc="Todos")

                return render_template("public/search.html", dist=distrilhas, conc=concelhos,
                    checked=lista_entidades, select_dist="Todos", select_conc="Todos",
                    results=results, count=len(results))

        # Filter search
        elif request.form["search-by"] == "filters":            
            subtipos = request.form.getlist("subtipo")
            concelho = request.form.get("concelho")
            distrilha = request.form.get("distrilha")
            
            # Ensure at least one type of entity-filter was selected
            if not subtipos:
                flash("Seleccione pelo menos um tipo de entidade para pesquisar.", "error")
                return render_template("public/search.html", dist=distrilhas, conc=concelhos,
                    checked=subtipos, select_dist=distrilha, select_conc=concelho)
            
            # Valid filters were selected - query the database and present results
            else:                
                # Filter by location if location was selected, otherwise show results for all locations.
                # If both concelho and distrilha were selected, filter only by concelho (and ignore distrilha)
                if concelho != "Todos":
                    # Merge selected filters and location into a new list (location at [0], then types of entities)
                    filters = subtipos.copy()
                    filters.insert(0, concelho)
                    
                    # Search the database according to selected filters
                    # (location is substituted in first placeholder "municipio",
                    # followed by a variable number of types of entities in "subtipo")
                    results = query_db("""SELECT * FROM places
                        JOIN contacts USING (id)
                        JOIN territory USING (code)
                        WHERE municipio = %s AND subtipo IN ({}) ORDER BY nome"""
                        .format(", ".join(["%s"]*len(subtipos))), filters)
                        # for use of .FORMAT see https://pyformat.info/
                        # https://stackoverflow.com/questions/1309989/parameter-substitution-for-a-sqlite-in-clause
                        # https://www.reddit.com/r/Python/comments/2ckv0y/sqlite_where_in_with_a_variable_number_of_criteria/

                elif distrilha != "Todos":
                    filters = subtipos.copy()
                    filters.insert(0, distrilha)

                    results = query_db("""SELECT * FROM places
                        JOIN contacts USING (id)
                        JOIN territory USING (code)
                        WHERE distrilha = %s AND subtipo IN ({}) ORDER BY nome"""
                        .format(", ".join(["%s"]*len(subtipos))), filters)

                else:
                    results = query_db("""SELECT * FROM places
                        JOIN contacts USING (id)
                        JOIN territory USING (code)
                        WHERE subtipo IN ({}) ORDER BY nome"""
                        .format(", ".join(["%s"]*len(subtipos))), subtipos)

                return render_template("public/search.html", dist=distrilhas, conc=concelhos,
                    checked=subtipos, select_dist=distrilha, select_conc=concelho,
                    results=results, count=len(results))


# Update filter dropdown menus in real time via network request from JavaScript
# https://towardsdatascience.com/talking-to-python-from-javascript-flask-and-the-fetch-api-e0ef3573c451
@app.route("/filter/<scope>/<location>")    # only accept GET requests (default)
def filter(scope, location):

    # User picked an option from "Distritos/Ilhas" dropdown menu
    if scope == "dist":

        if location != "Todos":
            try:
                # Try to load location data from pre-existing json file
                with open(f"app/static/json/locations.json", "r") as read_file:
                    locations = json.load(read_file)
            except:
                # Otherwise query the database and create a new json file with location data
                raw_list = query_db("""SELECT municipio, distrilha FROM territory WHERE distrilha IN
                    (SELECT DISTINCT distrilha FROM territory ORDER BY distrilha)
                    ORDER BY municipio""")
                
                # (convert returned dictionary of row objects into a dictionary of lists of strings)
                # https://www.kite.com/python/answers/how-to-append-an-element-to-a-key-in-a-dictionary-with-python
                locations = defaultdict(list)
                for municipio in raw_list:
                    locations[municipio["distrilha"]].append(municipio["municipio"])

                # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
                # https://realpython.com/python-json/
                with open(f"app/static/json/locations.json", "w") as write_file:
                    json.dump(locations, write_file)
            finally:
                # Send location data requested by JavaScript
                return jsonify(locations)   # serialize and use JSON headers. https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
        
        # Special case: user picked "Todos" from "Distritos/Ilhas" dropdown menu
        elif location == "Todos":
            try:
                with open(f"app/static/json/municipalities.json", "r") as read_file:
                    municipalities = json.load(read_file)
            except:
                raw_list = query_db("SELECT municipio FROM territory ORDER BY municipio")
                municipalities = []
                for municipio in raw_list:
                    municipalities.append(municipio["municipio"])
                
                with open(f"app/static/json/municipalities.json", "w") as write_file:
                    json.dump(municipalities, write_file)
            finally:
                return jsonify(municipalities)
                
    # User picked an option from "Concelhos" dropdown menu
    elif scope == "conc":

        try:
            # Get corresponding distrilha from database, convert row object to string and serialize to json
            for row_obj in query_db("SELECT distrilha FROM territory WHERE municipio = %s", [location]):
                result_str = row_obj["distrilha"]
            return jsonify(result_str)
        
        # Error handling: <location> provided in URL not valid, go to index page without querying database
        except:
            return redirect("/")
    
    # Error handling: <scope> provided in URL not valid, go to index page without making any changes
    else:
        return redirect("/")
