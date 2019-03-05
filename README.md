# Ablog

![quokka](https://github.com/rochacbruno/quokka/raw/master/docs/emoji_small.png)

## The ... in the world

Ablog is a Content Management Framework written in Python.

Ablog is a lightweight framework to build blogs for now maybe forever.

Ablog is not finished, more features to be implemented and more bugs to be fixed(hope not)

The most important : it is powered by Python and Flask.

## Features(to be implemented)

- :black_square_button: the search button
- :black_square_button: signup confirm email
- :black_square_button: user profile's avater
- :black_square_button: define hotest posts
- :black_square_button: forget password/ reset password

## Quick Start


> NOTE: QuokkaCMS requires Python 3.7+


### Run locally

```bash
git clone https://github.com/rochacbruno/quokka
cd quokka
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

flask initdb
flask fakedata
flask run

```

then access http://localhost:5000.


# Start contributing right now!