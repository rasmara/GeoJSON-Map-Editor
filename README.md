# GeoJSON Map Editor

Interactive google map interface to import, edit and update GeoJSON data.

## Steps to Run the project locally.


```sh
$ git clone https://github.com/rasmara/GeoJSON-Map-Editor.git

```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
```

Get into project directory:

```sh
$ cd GeoJSON-Map-Editor
```

create a ```.env``` file to load environment variables:

provide GOOGLE_MAPS_API_KEY

```sh
DEBUG=True
GOOGLE_MAPS_API_KEY=

```

Then install the dependencies:

```sh
pip install -r requirements.txt
```

Once, installation completes, Run the database migrations to create the database schema
```sh

$ python manage.py makemigrations

$ python manage.py migrate

```

Run project

```sh
$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/accounts/login`.
