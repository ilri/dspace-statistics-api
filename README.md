# CGSpace Statistics API
Written and tested in Python 3.6. SolrClient (0.2.1) does not currently run in Python 3.7.0.

## Installation
Create a virtual environment and run it:

    $ virtualenv -p /usr/bin/python3.6 venv
    $ . venv/bin/activate
    $ pip install falcon gunicorn SolrClient
    $ gunicorn app:api

