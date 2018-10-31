# DSpace Statistics API [![Build Status](https://travis-ci.org/ilri/dspace-statistics-api.svg?branch=master)](https://travis-ci.org/ilri/dspace-statistics-api)
DSpace versions 4.0 and up include a [REST API](https://wiki.duraspace.org/display/DSDOC5x/REST+API) that allows the repository to be queried programmatically. The API exposes information about communities, collections, items, and bitstreams, but not item views or downloads. This project contains a lightweight indexer and a web application to make the view and download statistics available via a simple REST API that can be deployed simultaneously with DSpace's own.

You can read more about the Solr queries used to gather the item view and download statistics on the [DSpace wiki](https://wiki.duraspace.org/display/DSPACE/Solr).

## Requirements

- Python 3.5+
- PostgreSQL version 9.5+ (due to [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT))
- DSpace 4+ with [Solr usage statistics enabled](https://wiki.duraspace.org/display/DSDOC5x/SOLR+Statistics)

## Installation and Testing
Create a Python virtual environment and install the dependencies:

    $ python -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

Set up the environment variables for Solr and PostgreSQL:

    $ export SOLR_SERVER=http://localhost:8080/solr
    $ export DATABASE_NAME=dspacestatistics
    $ export DATABASE_USER=dspacestatistics
    $ export DATABASE_PASS=dspacestatistics
    $ export DATABASE_HOST=localhost

Index the Solr statistics core to populate the PostgreSQL database:

    $ python -m dspace_statistics_api.indexer

Run the REST API:

    $ gunicorn dspace_statistics_api.app

Test to see if there are any statistics:

    $ curl 'http://localhost:8000/items?limit=1'

## Deployment
There are example systemd service and timer units in the `contrib` directory. The API service listens on localhost by default so you will need to expose it publicly using a web server like nginx.

An example nginx configuration is:

```
server {
    #...

    location ~ /rest/statistics/?(.*) {
        access_log /var/log/nginx/statistics.log;
        proxy_pass http://statistics_api/$1$is_args$args;
    }
}

upstream statistics_api {
    server 127.0.0.1:5000;
}
```

This would expose the API at `/rest/statistics`.

## Using the API
The API exposes the following endpoints:

  - GET `/items` — return views and downloads for all items that Solr knows about¹. Accepts `limit` and `page` query parameters for pagination of results.
  - GET `/item/id` — return views and downloads for a single item (*id* must be a positive integer). Returns HTTP 404 if an item id is not found.

¹ We are querying the Solr statistics core, which technically only knows about items that have either views or downloads.

## Todo

- Add API documentation
- Close DB connection when gunicorn shuts down gracefully
- Better logging
- Tests
- Check if database exists (try/except)
- Version API
- Use JSON in PostgreSQL
- Switch to [Python 3.6+ f-string syntax](https://realpython.com/python-f-strings/)

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
