# SPDX-License-Identifier: GPL-3.0-only

import os

# Check if Solr connection information was provided in the environment
SOLR_SERVER = os.environ.get("SOLR_SERVER", "http://localhost:8080/solr")

DATABASE_NAME = os.environ.get("DATABASE_NAME", "dspacestatistics")
DATABASE_USER = os.environ.get("DATABASE_USER", "dspacestatistics")
DATABASE_PASS = os.environ.get("DATABASE_PASS", "dspacestatistics")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")

# URL to DSpace Statistics API, which will be used as a prefix to API calls in
# the Swagger UI. An empty string will allow this to work out of the box in a
# local development environment, but for production it should be set to a value
# like "/rest/statistics", assuming that the statistics API is deployed next to
# the vanilla DSpace REST API.
DSPACE_STATISTICS_API_URL = os.environ.get("DSPACE_STATISTICS_API_URL", "")

VERSION = "1.4.4-dev"

# vim: set sw=4 ts=4 expandtab:
