# Simple sample Flask app to be deployed on Heroku

## Introduction
This is a Flask-based web app that supports a number of functionalities, including:
+ Authentication: Sign-in, Sign-up, Forgot password, etc
+ Blog CRUD: Can create blog posts using the Quill WYSIWYG
+ Categories and tags for blog posts
+ Save and Heart blog posts
+ Comment on posts and delete comments
+ Follow, and unfollow users
+ Change user role, suspend and unsuspend a user, delete user
+ Some good decorators such as account_state() that takes care if an account is suspended, if yes, it displays a cool page informing the user.
+ Adds a MASTER_PASSWORD for etc security for operations like suspending and deleting users and changing their roles
+ Edit your profile, change password, delete account.
+ Built-in HTTP error messages handlers
+ Has support for CSRF tokens to protect you against CSRF attacks

This samlpe app is built with the [Flask Application Factory Pattern](https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/) in mind alongside the use of [Blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints/#blueprints)

## Files and directories in the app

```console

.
├── app
│   ├── ajax
│   ├── api
│   ├── article
│   ├── auth
│   ├── data_retrieval.py
│   ├── decorators.py
│   ├── email.py
│   ├── errors
│   ├── exceptions.py
│   ├── forms.py
│   ├── functions.py
│   ├── __init__.py
│   ├── main
│   ├── models.py
│   ├── static
│   ├── templates
│   └── user
├── config.py
├── db.sqlite3
├── logs
│   ├── applog.log
├── migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── Procfile
├── README.md
├── requirements.txt
├── runtime.txt
├── tests.py
└── wsgi.py
```


## Usage

git clone or download this repository.

I assume you have Python and PIP installed on your machine. If not, please do.
Also you need to have Postgres database installed and running (if you donnot install or use Postgres db
, an sqlite db is used instead. You can use any db of choice you like. To learn more about that, please refer to Flask-Sqlalchemy and Sqlalechemy docs.)

```python
pip install requirements.txt
```

Flask enviroment variables:

On Linux
```console
foo@bar:~$ export FLASK_APP=wsgi.py
foo@bar:~$ export FLASK_ENV=development
```

On Windows
```console
foo@bar:~$ set FLASK_APP=wsgi.py
foo@bar:~$ set FLASK_ENV=development
```

If everything is good, now we have to map our db models to our db of choice. Luckly this is easly done:

```python
foo@bar:~$ flask db init
foo@bar:~$ flask db migrate
foo@bar:~$ flask db upgrade
```
At this point all should be good, now you just need to run the application:

```python
foo@bar:~$ flask run
```

## Deployment

I wrote a blog post on how to deploy a Flask app on Heroku [here](https://langcodex.herokuapp.com/posts/34) It deals specifically with deploying a chatbot, but it is the same. If you are interested in that you can check my Flask-based chatbot app source code, refer to [here](https://github.com/MurphyAdam/langandcode)

## Hint
To make an account associated with a specific email an admin, make sure you specify it in the ADMINS_EMAILS_WHITELIST in the config.py file. These emails are created with the Admin flag to give you permissins to CRUD. You can also make a user an admin or vise versa accessing their account.

To have your admin account confirmed automatically, in the __init__ of the User Class in the models.py 
set self.confirmed to True, recommended only for development purposes.
```python
self.confirmed = False
```

## Contributions
You are free to use and or modify this code as you wish, if you run into problems regarding the app, please issue a problem. Thank you

## Warranty
This app comes with absolutely no warranty whatsoever.

## License
[CC-BY](https://creativecommons.org/licenses/by/3.0/)
