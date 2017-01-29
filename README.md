The Scrap Scanner 5000
======================

The Scrap Scanner 5000 is a free service that lets you know when the car you are looking for has arrived at your local junkyard.

The Scrap Scanner 500 currently supports [LKQ Pick Your Part](https://www.lkqpickyourpart.com/) junk yards.
Tell us the make, model, or years of the car you need parts from and we will send you an email when one shows up at your favorite yard.

Setup
-----

The Scrap Scanner 5000 is designed to run on Python 3.6 and uses the [Flask framework](http://flask.pocoo.org/).

1. Create a virtualenv for python.

        python -m venv flask

2. Install python packages

        flask/bin/pip install flask
        flask/bin/pip install flask-script
        flask/bin/pip install flask-sqlalchemy
        flask/bin/pip install flask-migrate
        flask/bin/pip install flask-login
        flask/bin/pip install flask-mail
        flask/bin/pip install flask-wtf
        flask/bin/pip install bcrypt
        flask/bin/pip install beautifulsoup4
        
3. Install javascript packages

        npm update
