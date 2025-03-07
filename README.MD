# Dashboard Analytics App

This project is a web application for creating and managing dashboards with advanced data visualizations. It is built using Flask, SQLAlchemy, and Flask-Login.

## Project Structure

Dashboard Analytics App/
├── app/
│   ├── init.py
│   ├── auth/
│   │   ├── init.py
│   │   ├── models.py
│   │   ├── routes.py
│   ├── dashboard/
│   │   ├── init.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── forms.py
│   ├── data/
│   │   ├── init.py
│   │   ├── routes.py
│   ├── main/
│   │   ├── init.py
│   │   ├── routes.py
│   ├── api/
│   │   ├── init.py
│   │   ├── routes.py
│   ├── errors/
│   │   ├── init.py
│   │   ├── handlers.py
│   ├── assets.py
│   ├── cli.py
├── run.py
├── config.py
├── requirements.txt
├── templates/
│   ├── auth/
│   │   ├── login.html
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── create.html
│   │   ├── view.html
│   │   ├── edit.html
│   │   ├── widget_add.html
│   │   ├── widget_edit.html
│   │   ├── share.html
│   │   ├── data_sources.html
│   │   ├── data_source_add.html
│   ├── main/
│   │   ├── index.html
│   │   ├── settings.html
│   ├── errors/
│   │   ├── 404.html
│   │   ├── 500.html

### app/

This directory contains the main application package.

#### `__init__.py`

This file initializes the Flask application and sets up the necessary configurations, extensions, and blueprints.

### app/auth/

This directory contains the authentication blueprint for the application.

#### `__init__.py`

This file initializes the auth blueprint.

#### `models.py`

This file defines the database models for the auth blueprint. It includes the `User` model, which represents a user in the application.

#### `routes.py`

This file contains the route definitions for the auth blueprint. It includes routes for user login and logout.

### app/dashboard/

This directory contains the dashboard blueprint for the application.

#### `__init__.py`

This file initializes the dashboard blueprint.

#### `models.py`

This file defines the database models for the dashboard blueprint. It includes the `Dashboard`, `Widget`, `DataSource`, and `DashboardCollaborator` models.

#### `routes.py`

This file contains the route definitions for the dashboard blueprint. It includes routes for creating, viewing, editing, and deleting dashboards and widgets, sharing dashboards, and managing data sources.

#### `forms.py`

This file defines the forms used in the dashboard blueprint. It includes forms for creating and editing dashboards and widgets, and adding data sources.

### app/data/

This directory contains the data blueprint for the application.

#### `__init__.py`

This file initializes the data blueprint.

#### `routes.py`

This file contains the route definitions for the data blueprint. It includes routes for managing data sources.

### app/main/

This directory contains the main blueprint for the application.

#### `__init__.py`

This file initializes the main blueprint.

#### `routes.py`

This file contains the route definitions for the main blueprint. It includes routes for the home page, user settings, and logging out.

### app/api/

This directory contains the API blueprint for the application.

#### `__init__.py`

This file initializes the API blueprint.

#### `routes.py`

This file contains the route definitions for the API blueprint. It includes routes for accessing dashboard data via API.

### app/errors/

This directory contains the error handling blueprint for the application.

#### `__init__.py`

This file initializes the errors blueprint.

#### `handlers.py`

This file contains the error handlers for the application. It includes handlers for 404 and 500 errors.

### app/assets.py

This file contains the function for compiling assets (CSS, JS) for the application.

### app/cli.py

This file contains the CLI commands for the application. It includes a command for creating the database.

### run.py

This file is the entry point for running the Flask application. It creates an instance of the Flask application and runs it.

### config.py

This file contains the configuration settings for the Flask application. It includes settings for development and production environments.

### requirements.txt

This file lists the dependencies for the Flask application. Install the dependencies using `pip`:

```sh
pip install -r requirements.txt

templates/
This directory contains the HTML templates for the application.

auth/login.html
This file contains the login form template.

dashboard/
This directory contains the templates for the dashboard blueprint.

index.html - Displays the list of dashboards.
create.html - Form for creating a new dashboard.
view.html - Displays a specific dashboard.
edit.html - Form for editing a dashboard.
widget_add.html - Form for adding a new widget.
widget_edit.html - Form for editing a widget.
share.html - Form for sharing a dashboard.
data_sources.html - Displays the list of data sources.
data_source_add.html - Form for adding a new data source.
main/
This directory contains the templates for the main blueprint.

index.html - Home page template.
settings.html - User settings form template.
errors/
This directory contains the error templates.

404.html - Template for 404 Not Found error.
500.html - Template for 500 Internal Server Error.

Running the Application

To run the application, navigate to the project directory and execute the following command:
python run.py

Make sure to set the PYTHONPATH to include the root directory of your project if necessary:
set PYTHONPATH=c:/Users/mperz/Desktop/Dashboard Analytics App

Dependencies
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-Mail
Flask-CORS
Flask-WTF
Flask-Caching
Flask-Compress
Flask-Assets

Install the dependencies using pip:
pip install -r requirements.txt

License
This project is licensed under the MIT License.


This `README.md` file provides an overview of the project structure, routes, models, and instructions for running the application. Adjust the content as needed to fit your specific project details.
This `README.md` file provides an overview of the project structure, routes, models, and instructions for running the application. Adjust the content as needed to fit your specific project details.