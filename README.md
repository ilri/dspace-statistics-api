# DSpace Statistics API
A quick and dirty REST API to expose Solr view and download statistics for items in a DSpace repository.

Written and tested in Python 3.5, 3.6, and 3.7. Requires PostgreSQL version 9.5 or greater for [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT).

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
