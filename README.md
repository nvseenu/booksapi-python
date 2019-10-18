# Goal:

    This project provides below features through REST end points.
    - Finding external books using 3rd part api 'aniceandfireapi'
    - Creating, Updating , Deleting and Listing local books by using db

Technologies used: Python 3, Flask, Pytest, Postgres    

## External Books API
   This api provides below end point to get books

| Description | Endpoint |
| --- | --- |
| Get books by name | `http://localhost:5000/api/external-books?name=A Game of Thrones` |


## Books Api
   This api provides below end points
   
| Description | Endpoint |
| --- | --- |
| Create book | `http://localhost:5000/api/v1/books` | 
| Get book | `http://localhost:5000/api/v1/books/1` | 
| Update book | `http://localhost:5000/api/v1/books/1` |   
| Delete book | `http://localhost:5000/api/v1/books/1` |
| Get books | `http://localhost:5000/api/v1/books?name=A Game of Thrones` |   


## Setup the project (Ubuntu):
### Clone the project
```
> git clone https://github.com/nvseenu/booksapi-python.git
```

### Setup virtualenv 
```
> cd booksapi-python
> virtualenv -p /usr/bin/python3 venv
> . venv/bin/activate
```

### Install dependecies
```
> pip install -r requirements.txt
```

### Setup Postgres db
- Install Postgres 10 or above
- Create an user 'postgres' with password 'postgres'
- Create a database 'booksapi'
- Create a table 'books' using below query
```
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    isbn VARCHAR(50) NOT NULL,
    authors VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    number_of_pages INT DEFAULT 0,
    publisher VARCHAR(100),
    release_date DATE
);

```
If you have postgres running on some other machine, you can configure it in the below file
```config.py```

While updating config.py, please update config_qa.py as well. Config_qa.py file is used by
integration and endtoend tests.

### Run Flask
```
> export FLASK_APP=app.py
> export FLASK_ENV=development
> flask run
```
Flask app will be running now

### Run unit tests
```
> pytest tests/unit -s
```
### Run integration tests
```
> pytest tests/integration -s
```
### Run end to end tests
```
> pytest tests/endtoend -s
```


Note: This app runs with Flask dev server which is not suitable for production.
In order to use it in production, we should run this app with a server like Cherrypy, gunicorn
