from config import SQLITE_DB
import sqlite3

def database_connection():
    connection = sqlite3.connect(SQLITE_DB)
    # allow iterating over row results by column key
    connection.row_factory = sqlite3.Row

    return connection

# vim: set sw=4 ts=4 expandtab:
