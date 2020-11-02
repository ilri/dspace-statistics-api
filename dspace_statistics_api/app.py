import falcon

from .database import DatabaseManager
from .items import get_downloads, get_views
from .util import validate_items_post_parameters


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
        limit = req.get_param_as_int("limit", min_value=1, max_value=100) or 100
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

    @falcon.before(validate_items_post_parameters)
    def on_post(self, req, resp):
        """Handles POST requests"""

        # Build the Solr date string, ie: [* TO *]
        if req.context.dateFrom and req.context.dateTo:
            solr_date_string = f"[{req.context.dateFrom} TO {req.context.dateTo}]"
        elif not req.context.dateFrom and req.context.dateTo:
            solr_date_string = f"[* TO {req.context.dateTo}]"
        elif req.context.dateFrom and not req.context.dateTo:
            solr_date_string = f"[{req.context.dateFrom} TO *]"
        else:
            solr_date_string = "[* TO *]"

        # Helper variables to make working with pages/items/results easier and
        # to make the code easier to understand
        number_of_items: int = len(req.context.items)
        pages: int = int(number_of_items / req.context.limit)
        first_item: int = req.context.page * req.context.limit
        last_item: int = first_item + req.context.limit
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
        # So if we have a list items with 240 items:
        #
        #   1st set: items[0:100] would give items at indexes 0 to 99
        #   2nd set: items[100:200] would give items at indexes 100 to 199
        #   3rd set: items[200:300] would give items at indexes 200 to 239
        items_subset: list = req.context.items[first_item:last_item]

        views: dict = get_views(solr_date_string, items_subset)
        downloads: dict = get_downloads(solr_date_string, items_subset)

        # create a list to hold dicts of item stats
        statistics = list()

        # iterate over views dict to extract views and use the item id as an
        # index to the downloads dict to extract downloads.
        for k, v in views.items():
            statistics.append({"id": k, "views": v, "downloads": downloads[k]})

        message = {
            "currentPage": req.context.page,
            "totalPages": pages,
            "limit": req.context.limit,
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
