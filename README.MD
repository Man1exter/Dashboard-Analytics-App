# Dashboard Analytics App

This project is a web application for creating and managing dashboards with advanced data visualizations. It is built using Flask, SQLAlchemy, and Flask-Login.

## Project Structure

```
/
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── errors/
│   │   ├── __init__.py
│   │   └── handlers.py
│   ├── assets.py
│   └── cli.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── auth/
│   │   └── login.html
│   ├── main/
│   │   ├── dashboard.html
│   │   ├── edit_dashboard.html
│   │   ├── index.html
│   │   ├── new_dashboard.html
│   │   └── view_dashboard.html
│   └── base.html
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Features

-   **User Authentication**: Users can register, log in, and log out.
-   **Dashboard Management**: Authenticated users can create, view, edit, and delete their own dashboards.
-   **Public Dashboards**: Dashboards can be marked as public to be viewable by anyone.
-   **Asset Bundling**: CSS and JavaScript assets are bundled and minified.

## Setup and Installation

### Prerequisites

-   Python 3.x
-   pip

### Installation

1.  **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up the Flask application:**

    ```sh
    export FLASK_APP=run.py
    ```

5.  **Create the database:**

    ```sh
    flask create-db
    ```

## Running the Application

To run the application, execute the following command:

```sh
python run.py
```

The application will be available at `http://127.0.0.1:5000`.

## Dependencies

-   Flask
-   Flask-SQLAlchemy
-   Flask-Migrate
-   Flask-Login
-   Flask-Mail
-   Flask-CORS
-   Flask-WTF
-   Flask-Caching
-   Flask-Compress
-   Flask-Assets
-   PyJWT

## License

This project is licensed under the MIT License.