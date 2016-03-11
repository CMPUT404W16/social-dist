Installation
==============

Install required packages
-------------------------

In the first we need to install the all required package which listed in requirements.txt by follow commands::

    $ pip install -r requirements.txt

Note:

* **psycopg2 may not work on Mac**. If you do not need postgresql support, you can remove it in requirements.txt during the installation.


Database setup
----------------
`SQLITE` and `PostgreSQL` are two only types of Database can be using in this project.

Database initization
~~~~~~~~~~~~~~~~~~~~~
If you never run this program before, you have to initization the database first by follow commands::

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade

Database Upgrade
~~~~~~~~~~~~~~~~
Upgrade the Database by single command::

    python manage.py db Upgrade

Note: If unable to upgrade database, please delete the database then reinitization it. (**You will losing all data!**)

Database switching
~~~~~~~~~~~~~~~~~~~
If you want to using `PostgreSQL` instead of `SQLITE`, just put prefix `env DATABASE_URL={databse_url}` to any commands which you want to run such as::

    env DATABASE_URL={databse_url} python manage.py db init
    env DATABASE_URL={databse_url} python app.py

The `{database_url}` should be standard `SQLALCHEMY_DATABASE_URI`.

If no enviroment variable `DATABASE_URL` given, the program will using the default database url which can be found in `config.py`


Deployment
----------
To deploy the program by simple run follow command::

    python app.py

Now, you Fbook instantance should be able to reach at http://127.0.0.1:5000

Advanced Deployment
-------------------
Run Fbook with special configration.::

    env FLASK_CONFIG={config_name} python app.py

The `config_name` should be one of the config instance which defined in `config.py`


Example, run Fbook with PostgreSQL in production environment::

    env FLASK_CONFIG=production DATABASE_URL=... python app.py
