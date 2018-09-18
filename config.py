import os

# Check if Solr connection information was provided in the environment
SOLR_SERVER = os.environ.get('SOLR_SERVER', 'http://localhost:8080/solr')
SOLR_CORE = os.environ.get('SOLR_CORE', 'statistics')
