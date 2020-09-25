# DSpace Statistics API [![Build Status](https://travis-ci.org/ilri/dspace-statistics-api.svg?branch=master)](https://travis-ci.org/ilri/dspace-statistics-api) [![builds.sr.ht status](https://builds.sr.ht/~alanorth/dspace-statistics-api.svg)](https://builds.sr.ht/~alanorth/dspace-statistics-api?)
DSpace stores item view and download events in a Solr "statistics" core. This information is available for use in the various DSpace user interfaces, but is not exposed externally via any APIs. The DSpace 4/5/6 [REST API](https://wiki.lyrasis.org/display/DSDOC5x/REST+API), for example, only exposes information about communities, collections, item metadata, and bitstreams.

- If your DSpace is version 4 or 5, use [dspace-statistics-api v1.1.1](https://github.com/ilri/dspace-statistics-api/releases/tag/v1.1.1)
- If your DSpace is version 6+, use [dspace-statistics-api v1.2.0 or greater](https://github.com/ilri/dspace-statistics-api/releases/tag/v1.2.0)

This project contains an indexer and a [Falcon-based](https://falcon.readthedocs.io/) web application to make the statistics available via a simple REST API. You can read more about the Solr queries used to gather the item view and download statistics on the [DSpace wiki](https://wiki.lyrasis.org/display/DSPACE/Solr).

If you use the DSpace Statistics API please cite:

*Orth, A. 2018. DSpace statistics API. Nairobi, Kenya: ILRI. https://hdl.handle.net/10568/99143.*

## Requirements

- Python 3.6+
- PostgreSQL version 9.5+ (due to [`UPSERT` support](https://wiki.postgresql.org/wiki/UPSERT))
- DSpace with [Solr usage statistics enabled](https://wiki.lyrasis.org/display/DSDOC5x/SOLR+Statistics) (tested with 5.x)

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
  - POST `/items` — return views and downloads for an arbitrary list of items. Accepts `limit`, `page`, `dateFrom`, and `dateTo` parameters².
  - GET `/item/id` — return views and downloads for a single item (`id` must be a UUID). Returns HTTP 404 if an item id is not found.

The item id is the *internal* uuid for an item. You can get these from the standard DSpace REST API.

¹ We are querying the Solr statistics core, which technically only knows about items that have either views or downloads. If an item is not present here you can assume it has zero views and zero downloads, but not necessarily that it does not exist in the repository.

² POST requests to `/items` should be in JSON format with the following parameters:

```
{
    "limit": 100, // optional, integer between 0 and 100, default 100
    "page": 0, // optional, integer greater than 0, default 0
    "dateFrom": "2020-01-01T00:00:00Z", // optional, default *
    "dateTo": "2020-09-09T00:00:00Z", // optional, default *
    "items": [
        "f44cf173-2344-4eb2-8f00-ee55df32c76f",
        "2324aa41-e9de-4a2b-bc36-16241464683e",
        "8542f9da-9ce1-4614-abf4-f2e3fdb4b305",
        "0fe573e7-042a-4240-a4d9-753b61233908"
    ]
}
```

## TODO

- Better logging
- Version API (or at least include a /version endpoint?)
- Use JSON in PostgreSQL
- Add top items endpoint, perhaps `/top/items` or `/items/top`?
  - Actually we could add `/items?limit=10&sort=views`
- Make community and collection stats available
- Check IDs in database to see if they are deleted...

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
