# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Updated
- Update dependencies with `poetry update`
- Falcon 3.0.0, a minor change for us, but good to be using a current upstream
version

### Added
- GitHub Actions workflow to build and test the API

## [1.4.1] - 2021-01-14
### Changed
- Limit Solr query to UUIDs to avoid errors with unmigrated legacy stats (https://github.com/ilri/dspace-statistics-api/issues/12)

### Updated
- Dev dependencies

## [1.4.0] - 2020-12-27
### Added
- indexer.py now indexes views and downloads for communities and collections
- API endpoints for /communities, /community/id, /collections, and /collections/id
- Swagger UI interface on /swagger
- /status page which lists the API version

### Changed
- Add ORDER BY to /items resource to make sure results are returned
deterministically
- Use `fl` parameter in indexer to return only the field we are faceting by
- Minor refactoring of imports for PEP8 style
- More correct calculation of `totalPages` parameter in REST API response

## [1.3.2] - 2020-11-18
### Fixed
- Minor issue with limit parameter (> 0)
- Minor issue with limit parameter (<= 100)

### Changed
- Minor refactor in Solr bot filtering

### Updated
- Run poetry update

## [1.3.1] - 2020-10-06
### Changed
- Fix issue with requirements.txt caused by poetry's export

## [1.3.0] - 2020-10-06
### Changed
- Minor refactoring of indexer

### Added
- Ability to get statistics for arbitrary items and date ranges by POSTing a JSON-formatted request to /items as opposed to the current `GET /items` which returns pre-indexed all-time stats for all items

### Updated
- Run pipenv update, bringing minor updates to pytest, psycopg2-binary, etc

## [1.2.1] - 2020-03-02
### Changed
- Help text in API docs should reference UUIDs
- Sample SQL file for tests should use UUIDs

## [1.2.0] - 2020-03-02
### Changed
- Remove Python 3.5 from TravisCI because black requires Python >= 3.6
- Adapt API for DSpace 6+ UUIDs
  - This requires dropping the statistics database and re-indexing

### Updated
- Run pipenv update, bringing requests 2.23.0 and pytest 5.3.5

## [1.1.1] - 2019-11-27
### Added
- Configuration for automatic sorting of imports with isort
- Configuration for automatic code formatting with black

### Updated
- Run pipenv update, bringing psycopg2 2.8.4, requests 2.22.0, pytest 5.3.1,
and gunicorn 20.0.4

### Changed
- Use Ubuntu 18.04 "Bionic" for TravisCI builds
- Use Python 3.8.0 for pipenv
- Minor syntax issues highlighted by flake8

## [1.1.0] - 2019-05-05
### Updated
- Falcon 2.0.0 (@alanorth)

## [1.0.0] - 2019-04-15
### Added
- Build configuration for build.sr.ht

### Updated
- Run pipenv update, bringing pytest version 4.4.0, psycopg-binary 2.8.2, etc
- sr.ht and TravisCI configuration to disable emojis and animation to keep logs clean

### Changed
- Use vanilla requests library instead of SolrClient
- Use one-based paging in indexer output (for human readability)

## [0.9.0] - 2019-01-22
### Updated
- pytest version 4.0.0
- Fix indexing of sharded statistics cores (#10)
- Handle case of missing views/downloads gracefully

## [0.8.1] - 2018-11-14
### Changed
- README.md to recommend using vanilla Python virtual environments and pip instead of pipenv
- Regenerate pipenv environment to capture only direct dependencies

### Added
- `requirements-dev.txt` for installing development packages with pip

## [0.8.0] - 2018-11-11
### Changed
- Properly handle database connection errors

### Added
- API tests with pytest

## [0.7.0] - 2018-11-07
### Added
- Ability to configure PostgreSQL database port with DATABASE_PORT environment variable (defaults to 5432)
- Hound CI configuration to validate pull requests against PEP 8 code style with Flake8
- Configuration for [pipenv](https://pipenv.readthedocs.io/en/latest/)

### Changed
- Use a database management class with Python context management to automatically open/close connections and cursors

### Changed
- Validate code against PEP 8 style guide with Flake8

## [0.6.1] - 2018-10-31
### Added
- API documentation at root path (/)

## [0.6.0] - 2018-10-31
### Changed
- Refactor project structure (note breaking changes to API and indexing invocation, see contrib and README.md)

## [0.5.2] - 2018-10-28
### Changed
- Update library versions in requirements.txt

## [0.5.1] - 2018-10-24
### Changed
- Use Python's native json instead of ujson

## [0.5.0] - 2018-10-24
### Added
- Example nginx configuration to README.md

### Changed
- Don't initialize Solr connection in API

## [0.4.3] - 2018-10-17
### Changed
- Use pip install as script for Travis CI

### Improved
- Documentation for deployment and testing

## [0.4.2] - 2018-10-04
### Changed
- README.md introduction and requirements
- Use ujson instead of json
- Iterate directly on SQL cursor in `/items` route

### Fixed
- Logic error in SQL for item views

## [0.4.1] - 2018-09-26
### Changed
- Use `execute_values()` to batch insert records to PostgreSQL

## [0.4.0] - 2018-09-25
### Fixed
- Invalid OnCalendar syntax in dspace-statistics-indexer.timer
- Major logic error in indexer.py

## [0.3.2] - 2018-09-25
## Changed
- /item/id route now returns HTTP 404 if an item is not found

## [0.3.1] - 2018-09-25
### Changed
- Force SolrClient's kazoo dependency to version 2.5.0 to work with Python 3.7
- Add Python 3.7 to Travis CI configuration

## [0.3.0] - 2018-09-25
### Added
- requirements.txt for pip
- Travis CI build configuration for Python 3.5 and 3.6
- Documentation on using the API

### Changed
- The "all items" route from / to /items

## [0.2.1] - 2018-09-24
### Changed
- Environment settings in example systemd unit files
- Use psycopg2.extras.DictCursor for PostgreSQL connection

## [0.2.0] - 2018-09-24
### Changed
- Use PostgreSQL instead of SQLite because UPSERT support needs a very new libsqlite3 whereas it's already in PostgreSQL 9.5+

## [0.1.0] - 2018-09-24
### Changed
- Rename project to "DSpace Statistics API"
- Use read-only database connection in API
- Update systemd units for CGSpace→DSpace rename
- Use UPSERT to simplify database schema and Python logic

### Added
- Example systemd service and timer unit for indexer service
- Add top-level route to expose all item statistics

### Removed
- Ability to customize SOLR_CORE variable

## [0.0.4] - 2018-09-23
### Added
- Added example systemd unit file for API
- Added indexer.py to ingest views and downloads from Solr to a SQLite database

### Changed
- Refactor Solr configuration and connection
- /item route now expects id as part of the URI instead of a query parameter: /item/id
- View and download stats are now fetched from a SQLite database

## [0.0.3] - 2018-09-20
### Changed
- Refactor environment variables into config module
- Simplify Solr query for "downloads"
- Optimize Solr query by using rows=0
- Fix Solr queries for item views

## [0.0.2] - 2018-09-18
### Added
- Ability to get Solr parameters from environment (`SOLR_SERVER` and `SOLR_CORE`)

## [0.0.1] - 2018-09-18
- Initial release
