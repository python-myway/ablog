# Ablog

## Preview

![one picture here]()

## Introduction

~~Ablog is a Content Management Framework written in Python.~~:stuck_out_tongue_winking_eye:

Ablog is a lightweight framework to build blogs for now maybe forever.

Ablog is not finished, more features to be implemented and more bugs to be fixed(hope not :sob: ).

It is powered by [Python](https://www.python.org/) and [Flask](http://flask.pocoo.org/). :two_hearts:

## Quick Start

> NOTE: Ablog requires Python 3.7+.

```
# clone the project
git clone https://github.com/python-myway/ablog.git

# build a Python vitual environment
cd ablog
python3 -m venv venv

# activate the env and install requirements
source venv/bin/activate
pip3 install -r requirements.txt

# before you start the server, do some init.
mkdir logs
touch ablog.log
flask initdb
flask fakedata

# then you can run locally.
flask run

# then access http://localhost:5000.
# there are some fake people using ablog.
# the default user and passwd pairs are {'admin0': 'admin0', 'admin1': 'admin1',...'admin4': 'admin4'}

```

## Features(some are to be implemented)

- :ballot_box_with_check: signup/login
- :ballot_box_with_check: add/delete/check articles/categories
- :ballot_box_with_check: add/delete comments
- :ballot_box_with_check: enable/disable comment
- :ballot_box_with_check: follow/unfollow bloger
- :ballot_box_with_check: search article
- :ballot_box_with_check: manage personal profile
- :ballot_box_with_check: responsive website design
- :ballot_box_with_check: support rich text
- :black_square_button: the search button
- :black_square_button: signup confirm email
- :black_square_button: user profile
- :black_square_button: hotest posts
- :black_square_button: forget password / reset password button
- :black_square_button: related articles recommended (based on similar category)

## Tips

- all configs are located in ablog/settings.py.
- it's better to write a .flaskenv file in this dir, then put `FLASK_ENV=development` in the file or you can just type `export FLASK_ENV=development` in the cmd.

## 