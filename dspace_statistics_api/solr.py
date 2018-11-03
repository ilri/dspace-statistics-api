from .config import SOLR_SERVER
from SolrClient import SolrClient


def solr_connection():
    connection = SolrClient(SOLR_SERVER)

    return connection

# vim: set sw=4 ts=4 expandtab:
