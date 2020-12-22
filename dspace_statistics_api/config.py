import os

# Check if Solr connection information was provided in the environment
SOLR_SERVER = os.environ.get("SOLR_SERVER", "http://localhost:8080/solr")

DATABASE_NAME = os.environ.get("DATABASE_NAME", "dspacestatistics")
DATABASE_USER = os.environ.get("DATABASE_USER", "dspacestatistics")
DATABASE_PASS = os.environ.get("DATABASE_PASS", "dspacestatistics")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")

# SwaggerUI configuration

# URI path where the Swagger UI should be available (without trailing slash)
SWAGGERUI_URL = os.environ.get("SWAGGERUI_URL", "/swagger")
# URI path to the OpenAPI JSON schema
SWAGGERUI_SCHEMA_URL = os.environ.get("SWAGGERUI_SCHEMA_URL", "/docs/openapi.json")

VERSION = "1.4.0-dev"

# vim: set sw=4 ts=4 expandtab:
