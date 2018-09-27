# DSpace Statistics API
A simple REST API to expose Solr view and download statistics for items in a DSpace repository.

## Requirements

- Python 3.5+
- PostgreSQL version 9.5+ (due to [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT)).
- DSpace 4+ with [Solr usage statistics enabled](https://wiki.duraspace.org/display/DSDOC5x/SOLR+Statistics)

## Installation
Create a virtual environment and run it:

    $ python -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ gunicorn app:api

## Using the API
The API exposes the following endpoints:

  - GET `/items` — return views and downloads for all items that Solr knows about¹. Accepts `limit` and `page` query parameters for pagination of results.
  - GET `/item/id` — return views and downloads for a single item (*id* must be a positive integer). Returns HTTP 404 if an item id is not found.

¹ We are querying the Solr statistics core, which technically only knows about items that have either views or downloads.

## Todo

- Add API documentation
- Close up DB connection when gunicorn shuts down gracefully
- Better logging
- Tests

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
