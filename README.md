# CGSpace Statistics API
A quick and dirty REST API to expose Solr view and download statistics for items in a DSpace repository.

Written and tested in Python 3.6. SolrClient (0.2.1) does not currently run in Python 3.7.0.

## Installation
Create a virtual environment and run it:

    $ virtualenv -p /usr/bin/python3.6 venv
    $ . venv/bin/activate
    $ pip install falcon gunicorn SolrClient
    $ gunicorn app:api

## Todo

- Take a list of items (POST in JSON?)

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
