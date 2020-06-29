import os

# Check if Solr connection information was provided in the environment
SOLR_SERVER = os.environ.get("SOLR_SERVER", "http://localhost:8080/solr")

# vim: set sw=4 ts=4 expandtab:
