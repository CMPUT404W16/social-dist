# social-dist

##How to run
###Run local with default environment

Do

```
python app.py
```

###Run local with production environment

Do

```
env FLASK_CONFIG=production python app.py
```

If want to put psql database support, do

```
env DATABASE_URL={databse_url} FLASK_CONFIG=production python app.py
```

###Run on heroku
After push code to the heroku instance, the app will automaticly start by gunicorn.

####Limitations
The gunicorn does not support 503 error pages.

The only way to see the error msg on heroku is to use the logs console.
```
heroku logs -t
```

##Simple instruction to start

Once you clone this repo, you need to setup the virtual environment first.

cd to the project folder (It has a file called requirements.txt)

Do

    virtualenv env

Waiting for the virtual environment setup process...

After the setup process finish, type

    source env/bin/activate

    pip install -r requirenments.txt

Then pip will help you get all the packages we need.

In the case of installing any new package and you want to add the package to the requirement list, you can check the package list by typing

    pip freeze

If you want to update the requirement.txt file, type

    pip freeze > requirements.txt

--------------

Flask is simple to use when you want to upgrade your database.

If you do not have the migration folder at the root dir. You should run

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade

Then Flask will automatically add a migration folder and setup all the things for you.

If you already have a migration folder and the .sqlite file, run

    python manage.py db upgrade

We can talk about this part later.

