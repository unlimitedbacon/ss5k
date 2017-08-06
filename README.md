The Scrap Scanner 5000
======================

[The Scrap Scanner 5000](https://ss5k.unlimitedbacon.net/) is a free service that lets you know when the car you are looking for has arrived at your local junkyard.

The Scrap Scanner 500 currently supports [LKQ Pick Your Part](https://www.lkqpickyourpart.com/) junk yards.
Tell us the make, model, or years of the car you need parts from and we will send you an email when one shows up at your favorite yard.

Setup
-----

The Scrap Scanner 5000 is designed to run on Python 3.6 and uses the [Flask framework](http://flask.pocoo.org/).

1. Copy the example config and change things as needed.

        $ cp config.py.example config.py

2. Create a virtualenv for python.

        $ python -m venv flask

3. Install python packages

        $ flask/bin/pip install -r requirements.txt
        
4. Install javascript packages

        $ npm update

5. Setup the database.

        $ flask/bin/python
        >>> from app import db
        >>> db.create_all()
        
6. Import the list of junkyards. If using the default SQLite database you can do this easily with sqlite-browser. If on a production server running Postgres, do this from an SQL prompt.

        => \copy junkyard FROM 'junkyards.csv' DELIMITER ',' CSV HEADER;
        
7. Install and start a mail server as per your distribution's instructions.

8. Start the debug server

        $ ./manage.py runserver
