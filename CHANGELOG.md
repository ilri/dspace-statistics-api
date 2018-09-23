# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
