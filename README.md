# DSpace Statistics API
A quick and dirty REST API to expose Solr view and download statistics for items in a DSpace repository.

Written and tested in Python 3.5 and 3.6. SolrClient (0.2.1) does [not currently run in Python 3.7.0](https://github.com/moonlitesolutions/SolrClient/issues/79). Requires PostgreSQL version 9.5 or greater for [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT).

## Installation
Create a virtual environment and run it:

    $ virtualenv -p /usr/bin/python3.6 venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ gunicorn app:api

## Todo

- Add API documentation
- Close up DB connection when gunicorn shuts down gracefully
- Better logging
- Return HTTP 404 when item_id is nonexistent

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
