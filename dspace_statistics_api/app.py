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
                    "SELECT id, views, downloads FROM items LIMIT %s OFFSET %s",
                    [limit, offset],
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

    def on_post(self, req, resp):
        """Handles POST requests"""

        import json
        from .items import get_views
        from .items import get_downloads
        from .util import is_valid_date

        # Only attempt to read the POSTed request if its length is not 0 (or
        # rather, in the Python sense, if length is not a False-y value).
        if req.content_length:
            doc = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPBadRequest(
                title="Invalid request", description=f"Request body is empty."
            )

        # Parse date parameters from request body (will raise an HTTPBadRequest
        # from is_valid_date() if any parameters are invalid)
        req_dateFrom = (
            doc["dateFrom"]
            if "dateFrom" in doc and is_valid_date(doc["dateFrom"])
            else None
        )
        req_dateTo = (
            doc["dateTo"] if "dateTo" in doc and is_valid_date(doc["dateTo"]) else None
        )

        # Build the Solr date string, ie: [* TO *]
        if req_dateFrom and req_dateTo:
            solr_date_string = f"[{req_dateFrom} TO {req_dateTo}]"
        elif not req_dateFrom and req_dateTo:
            solr_date_string = f"[* TO {req_dateTo}]"
        elif req_dateFrom and not req_dateTo:
            solr_date_string = f"[{req_dateFrom} TO *]"
        else:
            solr_date_string = "[* TO *]"

        # Parse the limit parameter from the POST request body
        req_limit = doc["limit"] if "limit" in doc else 100
        if not isinstance(req_limit, int) or req_limit < 0 or req_limit > 100:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description=f'The "limit" parameter is invalid. The value must be an integer between 0 and 100.',
            )

        # Parse the page parameter from the POST request body
        req_page = doc["page"] if "page" in doc else 0
        if not isinstance(req_page, int) or req_page < 0:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description=f'The "page" parameter is invalid. The value must be at least 0.',
            )

        # Parse the list of items from the POST request body
        req_items = doc["items"] if "items" in doc else list()
        if not isinstance(req_items, list) or len(req_items) == 0:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description=f'The "items" parameter is invalid. The value must be a comma-separated list of item UUIDs.',
            )

        # Helper variables to make working with pages/items/results easier and
        # to make the code easier to understand
        number_of_items: int = len(req_items)
        pages: int = int(number_of_items / req_limit)
        first_item: int = req_page * req_limit
        last_item: int = first_item + req_limit
        # Get a subset of the POSTed items based on our limit. Note that Python
        # list slicing and indexing are both zero based, but the first and last
        # items in a slice can be confusing. See this ASCII diagram:
        #
        #                 +---+---+---+---+---+---+
        #                 | P | y | t | h | o | n |
        #                 +---+---+---+---+---+---+
        # Slice position: 0   1   2   3   4   5   6
        # Index position:   0   1   2   3   4   5
        #
        # So if we have a list req_items with 240 items:
        #
        #   1st set: req_items[0:100] would give items at indexes 0 to 99
        #   2nd set: req_items[100:200] would give items at indexes 100 to 199
        #   3rd set: req_items[200:300] would give items at indexes 200 to 239
        items_subset: list = req_items[first_item:last_item]

        views: dict = get_views(solr_date_string, items_subset)
        downloads: dict = get_downloads(solr_date_string, items_subset)

        # create a list to hold dicts of item stats
        statistics = list()

        # iterate over views dict to extract views and use the item id as an
        # index to the downloads dict to extract downloads.
        for k, v in views.items():
            statistics.append({"id": k, "views": v, "downloads": downloads[k]})

        message = {
            "currentPage": req_page,
            "totalPages": pages,
            "limit": req_limit,
            "statistics": statistics,
        }

        resp.status = falcon.HTTP_200
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
                        description=f'The item with id "{str(item_id)}" was not found.',
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
