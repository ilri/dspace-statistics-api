# SPDX-License-Identifier: GPL-3.0-only

import falcon
import psycopg

from .config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASS,
    DATABASE_PORT,
    DATABASE_USER,
)


class DatabaseManager:
    """Manage database connection."""

    def __init__(self):
        self._connection_uri = f"dbname={DATABASE_NAME} user={DATABASE_USER} password={DATABASE_PASS} host={DATABASE_HOST} port={DATABASE_PORT}"

    def __enter__(self):
        try:
            self._connection = psycopg.connect(
                self._connection_uri, row_factory=psycopg.rows.dict_row
            )
        except psycopg.OperationalError:
            title = "500 Internal Server Error"
            description = "Could not connect to database"
            raise falcon.HTTPInternalServerError(title, description)

        return self._connection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.close()


# vim: set sw=4 ts=4 expandtab:
