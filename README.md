# DSpace Statistics API [![Build Status](https://travis-ci.com/ilri/dspace-statistics-api.svg?branch=master)](https://travis-ci.com/ilri/dspace-statistics-api) [![builds.sr.ht status](https://builds.sr.ht/~alanorth/dspace-statistics-api.svg)](https://builds.sr.ht/~alanorth/dspace-statistics-api?)
DSpace stores item view and download events in a Solr "statistics" core. This information is available for use in the various DSpace user interfaces, but is not exposed externally via any APIs. The DSpace 4/5 [REST API](https://wiki.duraspace.org/display/DSDOC5x/REST+API), for example, only exposes information about communities, collections, item metadata, and bitstreams.

This project contains an indexer and a [Falcon-based](https://falcon.readthedocs.io/) web application to make the statistics available via a simple REST API. You can read more about the Solr queries used to gather the item view and download statistics on the [DSpace wiki](https://wiki.duraspace.org/display/DSPACE/Solr).

If you use the DSpace Statistics API please cite:

*Orth, A. 2018. DSpace statistics API. Nairobi, Kenya: ILRI. https://hdl.handle.net/10568/99143.*

## Requirements

- Python 3.5+
- PostgreSQL version 9.5+ (due to [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT))
- DSpace with [Solr usage statistics enabled](https://wiki.duraspace.org/display/DSDOC5x/SOLR+Statistics) (tested with 5.x)

## Installation
Create a Python virtual environment and install the dependencies:

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

## Running

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

## Testing
Install development packages using pip:

    $ pip install -r requirements-dev.txt

Run tests:

    $ pytest

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

  - GET `/` — return a basic API documentation page.
  - GET `/items` — return views and downloads for all items that Solr knows about¹. Accepts `limit` and `page` query parameters for pagination of results (`limit` must be an integer between 1 and 100, and `page` must be an integer greater than or equal to 0).
  - GET `/item/id` — return views and downloads for a single item (`id` must be a positive integer). Returns HTTP 404 if an item id is not found.

The item id is the *internal* id for an item. You can get these from the standard DSpace REST API.

¹ We are querying the Solr statistics core, which technically only knows about items that have either views or downloads. If an item is not present here you can assume it has zero views and zero downloads, but not necessarily that it does not exist in the repository.

## Todo

- Better logging
- Version API
- Use JSON in PostgreSQL
- Add top items endpoint, perhaps `/top/items` or `/items/top`?
- Make community and collection stats available
- Support [DSpace 6 UUIDs](https://jira.duraspace.org/browse/DS-1782)
- Switch to [Python 3.6+ f-string syntax](https://realpython.com/python-f-strings/)
- Check IDs in database to see if they are deleted...

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
