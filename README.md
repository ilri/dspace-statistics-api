# DSpace Statistics API
A quick and dirty REST API to expose Solr view and download statistics for items in a DSpace repository.

Written and tested in Python 3.6. SolrClient (0.2.1) does not currently run in Python 3.7.0. Requires SQLite version 3.24.0 or greater for [`UPSERT` support](https://www.sqlite.org/lang_UPSERT.html).

## Installation
Create a virtual environment and run it:

    $ virtualenv -p /usr/bin/python3.6 venv
    $ . venv/bin/activate
    $ pip install falcon gunicorn SolrClient
    $ gunicorn app:api

## Todo

- Add API documentation
- Close up DB connection when gunicorn shuts down gracefully
- Better logging
- Return HTTP 404 when item_id is nonexistent

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
