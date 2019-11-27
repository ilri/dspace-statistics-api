from .config import DATABASE_NAME
from .config import DATABASE_USER
from .config import DATABASE_PASS
from .config import DATABASE_HOST
from .config import DATABASE_PORT
import falcon
import psycopg2
import psycopg2.extras


class DatabaseManager:
    """Manage database connection."""

    def __init__(self):
        self._connection_uri = "dbname={} user={} password={} host={} port={}".format(
            DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_PORT
        )

    def __enter__(self):
        try:
            self._connection = psycopg2.connect(
                self._connection_uri, cursor_factory=psycopg2.extras.DictCursor
            )
        except psycopg2.OperationalError:
            title = "500 Internal Server Error"
            description = "Could not connect to database"
            raise falcon.HTTPInternalServerError(title, description)

        return self._connection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.close()


# vim: set sw=4 ts=4 expandtab:
