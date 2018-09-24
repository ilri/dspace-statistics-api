import os

# Check if Solr connection information was provided in the environment
SOLR_SERVER = os.environ.get('SOLR_SERVER', 'http://localhost:8080/solr')

DATABASE_NAME = os.environ.get('DATABASE_NAME', 'dspacestatistics')
DATABASE_USER = os.environ.get('DATABASE_USER', 'dspacestatistics')
DATABASE_PASS = os.environ.get('DATABASE_PASS', 'dspacestatistics')
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')

# vim: set sw=4 ts=4 expandtab:
