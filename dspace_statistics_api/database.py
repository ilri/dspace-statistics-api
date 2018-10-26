from .config import DATABASE_NAME
from .config import DATABASE_USER
from .config import DATABASE_PASS
from .config import DATABASE_HOST
import psycopg2, psycopg2.extras

def database_connection():
    connection = psycopg2.connect("dbname={} user={} password={} host='{}'".format(DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST), cursor_factory=psycopg2.extras.DictCursor)

    return connection

# vim: set sw=4 ts=4 expandtab:
