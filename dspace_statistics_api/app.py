import json
import math

import falcon
import psycopg2.extras
from falcon_swagger_ui import register_swaggerui_app

from .config import DSPACE_STATISTICS_API_URL, VERSION
from .database import DatabaseManager
from .stats import get_downloads, get_views
from .util import set_statistics_scope, validate_post_parameters


class RootResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        docs_html = (
            "<!DOCTYPE html>"
            "<html lang=\"en-US\">"
            "    <head>"
            "        <meta charset=\"UTF-8\">"
            "        <title>DSpace Statistics API</title>"
            "    </head>"
            "    <body>"
            f"        <h1>DSpace Statistics API {VERSION}</h1>"
            f"        <p>This site is running the <a href=\"https://github.com/ilri/dspace-statistics-api\" title=\"DSpace Statistics API project\">DSpace Statistics API</a>. For more information see the project's README.md or the interactive <a href=\"{DSPACE_STATISTICS_API_URL + '/swagger'}\">Swagger UI</a> built into this API.</p>"
            "    </body>"
            "</html"
        )

        resp.body = docs_html


class StatusResource:
    def on_get(self, req, resp):
        message = {"version": VERSION}

        resp.status = falcon.HTTP_200
        resp.media = message


class OpenAPIJSONResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        with open("dspace_statistics_api/docs/openapi.json", "r") as f:
            # Load the openapi.json schema
            data = json.load(f)

            # Swagger assumes your API is at the root of the current host unless
            # you configure a "servers" block in the schema. The problem is that
            # I want this to work in both development and production, so we need
            # to make this configurable.
            #
            # If the DSPACE_STATISTICS_API_URL is configured then we will add a
            # server entry to the openapi.json schema before sending it.
            if DSPACE_STATISTICS_API_URL != "":
                data["servers"] = [{"url": DSPACE_STATISTICS_API_URL}]

            resp.body = json.dumps(data)


class AllStatisticsResource:
    @falcon.before(set_statistics_scope)
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        limit = req.get_param_as_int("limit", min_value=1, max_value=100) or 100
        page = req.get_param_as_int("page", min_value=0) or 0
        offset = limit * page

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                # get total number of communities/collections/items so we can estimate the pages
                cursor.execute(f"SELECT COUNT(id) FROM {req.context.statistics_scope}")
                pages = math.ceil(cursor.fetchone()[0] / limit)

                # get statistics and use limit and offset to page through results
                cursor.execute(
                    f"SELECT id, views, downloads FROM {req.context.statistics_scope} ORDER BY id LIMIT %s OFFSET %s",
                    [limit, offset],
                )

                # create a list to hold dicts of stats
                statistics = list()

                # iterate over results and build statistics object
                for result in cursor:
                    statistics.append(
                        {
                            "id": str(result["id"]),
                            "views": result["views"],
                            "downloads": result["downloads"],
                        }
                    )

        message = {
            "currentPage": page,
            "totalPages": pages,
            "limit": limit,
            "statistics": statistics,
        }

        resp.media = message

    @falcon.before(set_statistics_scope)
    @falcon.before(validate_post_parameters)
    def on_post(self, req, resp):
        """Handles POST requests.

        Uses two `before` hooks to set the statistics "scope" and validate the
        POST parameters. The "scope" is the type of statistics we want, which
        will be items, communities, or collections, depending on the request.
        """

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
        number_of_elements: int = len(req.context.elements)
        pages: int = math.ceil(number_of_elements / req.context.limit)
        first_element: int = req.context.page * req.context.limit
        last_element: int = first_element + req.context.limit
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
        # So if we have a list of items with 240 items:
        #
        #   1st set: items[0:100] would give items at indexes 0 to 99
        #   2nd set: items[100:200] would give items at indexes 100 to 199
        #   3rd set: items[200:300] would give items at indexes 200 to 239
        elements_subset: list = req.context.elements[first_element:last_element]

        views: dict = get_views(
            solr_date_string, elements_subset, req.context.views_facet_field
        )
        downloads: dict = get_downloads(
            solr_date_string, elements_subset, req.context.downloads_facet_field
        )

        # create a list to hold dicts of stats
        statistics = list()

        # iterate over views dict to extract views and use the element id as an
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


class SingleStatisticsResource:
    @falcon.before(set_statistics_scope)
    def on_get(self, req, resp, id_):
        """Handles GET requests"""

        # Adapt Python’s uuid.UUID type to PostgreSQL’s uuid
        # See: https://www.psycopg.org/docs/extras.html
        psycopg2.extras.register_uuid()

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                cursor = db.cursor()
                cursor.execute(
                    f"SELECT views, downloads FROM {req.context.database} WHERE id=%s",
                    [str(id_)],
                )
                if cursor.rowcount == 0:
                    raise falcon.HTTPNotFound(
                        title=f"{req.context.statistics_scope} not found",
                        description=f'The {req.context.statistics_scope} with id "{str(id_)}" was not found.',
                    )
                else:
                    results = cursor.fetchone()

                    statistics = {
                        "id": str(id_),
                        "views": results["views"],
                        "downloads": results["downloads"],
                    }

                    resp.media = statistics


api = application = falcon.API()
api.add_route("/", RootResource())
api.add_route("/status", StatusResource())

# Item routes
api.add_route("/items", AllStatisticsResource())
api.add_route("/item/{id_:uuid}", SingleStatisticsResource())

# Community routes
api.add_route("/communities", AllStatisticsResource())
api.add_route("/community/{id_:uuid}", SingleStatisticsResource())

# Collection routes
api.add_route("/collections", AllStatisticsResource())
api.add_route("/collection/{id_:uuid}", SingleStatisticsResource())

# Route to the Swagger UI OpenAPI schema
api.add_route("/docs/openapi.json", OpenAPIJSONResource())

# Path to host the Swagger UI. Keep in mind that Falcon will add a route for
# this automatically when we register Swagger and the path will be relative
# to the Falcon app like all other routes, not the absolute root.
SWAGGERUI_PATH = "/swagger"

# The *absolute* path to the OpenJSON schema. This must be absolute because
# it will be requested by the client and must resolve absolutely. Note: the
# name of this variable is misleading because it is actually the schema URL
# but we pass it into the register_swaggerui_app() function as the api_url
# parameter.
SWAGGERUI_API_URL = f"{DSPACE_STATISTICS_API_URL}/docs/openapi.json"

register_swaggerui_app(
    api,
    SWAGGERUI_PATH,
    SWAGGERUI_API_URL,
    config={
        "supportedSubmitMethods": ["get", "post"],
    },
    uri_prefix=DSPACE_STATISTICS_API_URL,
)

# vim: set sw=4 ts=4 expandtab:
