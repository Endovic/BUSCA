# **_BUSCA!_** Find my lost pet
#### Video Demo: [watch me!](https://www.youtube.com/watch?v=Mm54BjIIT1U)
### Description
_BUSCA!_ is a web platform for people who have lost their pets. It gathers in one place a range of useful resources for conducting a search operation successfully.

The aim of this project is ultimately to help getting stray pets reunited with their families.
### Scope
The _BUSCA!_ project targets the community and territory of Portugal, and consequently the language of the website is Portuguese.
## Structure and functionality
The website features:
* an **index** page that displays a hero image and gives access to the **main interface** with the following options:
  * two expandable sections with information on _how_ and _where_ to search, including links to relevant third-party websites (e.g. lost-and-found listings),
  * a link to a search tool (_see below_),
  * a link for visitors to get in touch and/or contribute to the project (_see below_);
* a **search** page with a tool for finding institutions that are likely to detect or may be housing a stray pet, such as: animal control services, animal welfare organizations, animal shelters, and vets. This tool is connected to a database (_see below_) and allows to:
  * search by name (full-text search),
  * search by filters:
    * county
    * municipality
    * type of institution
  * obtain the institutions' contact details:
    * physical address
    * phone number
    * email address
  * visit the institutions' homepage or social media;
* a **contact** page with a form allowing visitors to submit messages/comments/questions - these are stored in a database (_see below_);
* an **about** page with details about the project, its nature, context and purpose;
* a **privacy** page containing the website's privacy statement.

Each page features a **header** with a logo that links to the _index_ page, and a **footer** with links to the _about_, _contact_ and _privacy_ pages.

The _search_ page can be accessed from the main interface and from both expandable sections on the _index_ page.
## Database
Data is stored and managed through a relational database using the SQLite engine. It contains hundreds of contacts of relevant institutions based in Portugal, and keeps growing.

The database contains 22 tables as follows:
* table `contacts` stores each institution's name, type, contact details and date of update;
* table `territory` lists all the municipalities, counties and regions of Portugal;
* table `places` relates each institution with its location in the territory;
* table `messages` logs the subject and content of messages submitted by visitors to the website, optionally the visitor's name and email address (not required), and date/time of submission;
* table `admin` stores the login credentials for accessing the admin area (_see below_);
* table `changes` logs every admin change to the database (add new record, update record, delete record), and date/time of execution;
* table `sqlite_sequence` (created internally for management of primary keys);
* 15 tables supporting the `FTS5` virtual table module that provides full-text search functionality;

Plus 6 triggers to keep the virtual tables' indices up to date.
## Usage - Search tool
> **Note**: "name search" and "filter search" are independent from each other and use different submit buttons. It was a design choice to keep the search mechanism simple and robust and independent from any scripts, according to the principles of progressive enhancement, to ensure that as many users as possible can access the core functionalities of the website. Currently, search results are not dynamically updated when a word is typed on the search bar or a filter is selected. The aim is to implement this feature in the future using unobtrusive JavaScript.
#### Name search 
A name search performs a case-independent, diacritic-agnostic, full-text search on the database and presents all records whose name matches or contains the search term submitted by the user. If the search has multiple terms, matching results must contain all of them (in any order).

Name searches using Boolean expressions are possible with the operators `NOT`, `AND`, `OR` (case sensitive). However, each Boolean operator must be surrounded by search terms otherwise an error message is flashed.

Special characters are escaped, so any other advanced query syntax (e.g. exact-match phrases, prefixes/suffixes) has no effect.

An error message is flashed if a submitted search is empty or does not contain any alphanumeric characters.
#### Filter search
Geographical filters (county, municipality) are selection dropdown menus with the option `'All'` selected by default.

When the user selects a county from the dropdown menu, the content of the dependent dropdown menu is updated automatically to list only the municipalities that belong to the selected county. The reverse is also true: selecting first any municipality will result in the automatic selection of its respective county.

Category filters (animal shelter, veterinary practice, etc.) appear as clickable buttons, but in reality are labels for invisible checkboxes that are unchecked by default.

At least one category filter must be checked when submitting a filter search otherwise an error message is flashed.

A filter search submitted with all category filters checked and the option `"All"` selected for both geographical filters will get all records in the database.

The user's choice of filters is remembered and rendered between consecutive searches for as long as the user remains on the search page.
#### Search results
Upon submitting a valid search, a count of matching records in the database is displayed followed by the results listed in alphabetical order.

Results are presented in collapsed form, i.e., only the name, type and location of the institution is shown. The user can click on an arrowhead to expand each record individually and reveal its contact details and links to existing homepage/social media, or click on a `'View all'` button to expand/collapse all records simultaneously.

The user can click on a `'Copy email'` button to copy an email address to clipboard (to facilitate sending email queries to several institutions at the same time).
## Management - Admin area
The admin area allows for the convenient management of records in the database directly from the browser. It features:
* a **login** page with server-side authentication;
* a **dashboard** with links to:
  * a **new record** page with a form for adding a new record and saving it to the database;
  * an **update record** page that allows to search for a record by name and either update its details or delete it from the database;
  * a **full record list** page that displays the total number of records in the database and a sortable table presenting each record's full details.

Each page in the admin area features a **footer** with a link for logout (redirects to the _login_ page) and a link to the website's _index_ page.
## Security
For security reasons, admin passwords are stored as salted hashes in the database.

All `POST` requests are protected by CSRF tokens.
## Development
This project was built as a Flask application using Python (3.8.3) and JavaScript. The application's structure follows the package method, which allows working with multiple logical files and provides more flexibility for scaling up in the future.

Sass was used to pre-process entirely "handcrafted" CSS style sheets.

The code was written with Visual Studio Code and the website has been tested in Firefox (86.0), Chrome (89.0.4389.82), and Edge (89.0.774.45) browsers.

Table sorting is powered by a [third-party](https://www.kryogenix.org/code/browser/sorttable/) JavaScript library: `sorttable.js`.

All `svg`/`png` icons and logos were custom-designed in Adobe Illustrator CS6.

Favicons generated by [realfavicongenerator.net](https://realfavicongenerator.net/).

All `jpg` pictures by [Joana Meneses - Photography](https://www.facebook.com/JoanaMeneses.Photography/).
### File overview
```
.
|--- app
|     |--- static
|     |     |--- css
|     |     |     \ admin_styles.scss
|     |     |     \ styles.scss
|     |     |     \ ...
|     |     |--- favicon \ ...
|     |     |--- fonts \ ...
|     |     |--- img \ ...
|     |     |--- js
|     |     |     \ contact_behavior.js
|     |     |     \ index_behavior.js
|     |     |     \ search_behavior.js
|     |     |     \ ...
|     |     |--- json
|     |           \ locations.json
|     |           \ municipalities.json
|     |
|     |--- templates
|     |     |--- admin
|     |     |     \ adminlayout.html
|     |     |     \ dashboard.html
|     |     |     \ list.html
|     |     |     \ login.html
|     |     |     \ new.html
|     |     |     \ update.html
|     |     |--- public
|     |           \ about.html
|     |           \ contact.html
|     |           \ index.html
|     |           \ layout.html
|     |           \ privacy.html
|     |           \ search.html
|     |
|     \ __init__.py
|     \ admin_views.py
|     \ dbconnect.py
|     \ views.py
|
\ README.md
\ requirements.txt
\ run.py
```
#### Files written for this project:
* `\run.py`: entry point for launching the Flask app - must be located outside the directory that contains the application package (`\app`).

Running the app requires setting up an environment variable that tells Flask where to find the application instance: 
```
FLASK_APP = "run.py"
```
The app can then be run with the command:
```
flask run
```
* `app\__init__.py`: package constructor that creates the application object and pulls all the application components together. It also implements CSRF protection for the whole app.
* `app\views.py`: implements routes and responses to all public requests to the application. It handles name searches, filter searches and saves user messages to the database. It also handles network requests from JavaScript for updating dropdown menus in real time.
* `app\admin_views.py`: handles responses to all admin requests, namely retrieving, adding, updating or deleting records from the database, and keeps a log of them. It also handles admin login authentication.
* `app\dbconnect.py`: configures the connection to the database and implements helper functions for carrying out database queries.
* `static\js\index_behavior.js`: reacts to user interaction by showing/hiding expandable sections and their content. Also manages margins, navigation controls and scrolling on the index page.
* `static\js\search_behavior.js`: listens to changes to selection in dropdown menus and updates the options in the dependent menu by fetching `json` data from the server. Also deals with copying email addresses to clipboard, toggling view modes for results, and scrolling on the search page.
* `static\js\contact_behavior.js`: manages scrolling on the contact page.
* `static\json\locations.json`, `municipalities.json`: contain dictionaries and lists of locations used by JavaScript to update dropdown menus. These files are created once by the server and kept for reuse to avoid repeatedly querying the database.
* `static\css\styles.scss`, `admin_styles.scss`: contain most of the styles for public and admin pages - each Sass file is compiled to a CSS style sheet that gets linked to the HTML template. Media queries and other techniques are used to ensure a responsive design.
* `templates\public\layout.html`, `admin\admin_layout.html`: base templates for public and admin pages respectively.
* `templates\public\index.html`, `search.html`, `contact.html`, `about.html`, `privacy.html`: child templates for public pages.
* `templates\admin\login.html`, `dashboard.html`, `new.html`, `update.html`, `list.html`: child templates for admin pages.
* `requirements.txt`: lists all the libraries installed on the project's virtual environment during development (facilitates running the code on another system).
### Next steps
1. Publish to the World Wide Web. Domain name: `busca.website`
2. Implement the automatic sending of emails to admins when visitors submit messages via contact form
3. Improve error handling and reporting
4. Keep updating and enlarging the database to ensure its full effectiveness at a national scale 
5. Translate the website to English for improved accessibility by foreigners currently in Portugal
6. Add more features to the search tool
---
Submitted as final project to Harvard's CS50x 2021
