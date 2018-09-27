# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2018-09-26
### Changed
- Use execute_values() to batch insert records to PostgreSQL

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
