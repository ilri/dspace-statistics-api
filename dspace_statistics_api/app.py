import falcon

from .database import DatabaseManager


class RootResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        with open("dspace_statistics_api/docs/index.html", "r") as f:
            resp.body = f.read()


class AllItemsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        limit = req.get_param_as_int("limit", min_value=0, max_value=100) or 100
        page = req.get_param_as_int("page", min_value=0) or 0
        offset = limit * page

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                # get total number of items so we can estimate the pages
                cursor.execute("SELECT COUNT(id) FROM items")
                pages = round(cursor.fetchone()[0] / limit)

                # get statistics and use limit and offset to page through results
                cursor.execute(
                    "SELECT id, views, downloads FROM items LIMIT {} OFFSET {}".format(
                        limit, offset
                    )
                )

                # create a list to hold dicts of item stats
                statistics = list()

                # iterate over results and build statistics object
                for item in cursor:
                    statistics.append(
                        {
                            "id": str(item["id"]),
                            "views": item["views"],
                            "downloads": item["downloads"],
                        }
                    )

        message = {
            "currentPage": page,
            "totalPages": pages,
            "limit": limit,
            "statistics": statistics,
        }

        resp.media = message


class ItemResource:
    def on_get(self, req, resp, item_id):
        """Handles GET requests"""

        import psycopg2.extras

        # Adapt Python’s uuid.UUID type to PostgreSQL’s uuid
        # See: https://www.psycopg.org/docs/extras.html
        psycopg2.extras.register_uuid()

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT views, downloads FROM items WHERE id=%s", [str(item_id)]
                )
                if cursor.rowcount == 0:
                    raise falcon.HTTPNotFound(
                        title="Item not found",
                        description='The item with id "{}" was not found.'.format(
                            str(item_id)
                        ),
                    )
                else:
                    results = cursor.fetchone()

                    statistics = {
                        "id": str(item_id),
                        "views": results["views"],
                        "downloads": results["downloads"],
                    }

                    resp.media = statistics


api = application = falcon.API()
api.add_route("/", RootResource())
api.add_route("/items", AllItemsResource())
api.add_route("/item/{item_id:uuid}", ItemResource())

# vim: set sw=4 ts=4 expandtab:
