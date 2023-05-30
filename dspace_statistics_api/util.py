# SPDX-License-Identifier: GPL-3.0-only

import datetime
import json
import re

import falcon
import requests

from .config import SOLR_SERVER


def get_statistics_shards():
    """Enumerate the cores in Solr to determine if statistics have been sharded into
    yearly shards by DSpace's stats-util or not (for example: statistics-2018).

    Returns:
        str:A list of Solr statistics shards separated by commas.
    """

    # Initialize an empty list for statistics core years
    statistics_core_years = []

    # URL for Solr status to check active cores
    solr_query_params = {"action": "STATUS", "wt": "json"}
    solr_url = SOLR_SERVER + "/admin/cores"
    res = requests.get(solr_url, params=solr_query_params)

    if res.status_code == requests.codes.ok:
        data = res.json()

        # Iterate over active cores from Solr's STATUS response (cores are in
        # the status array of this response).
        for core in data["status"]:
            # Pattern to match, for example: statistics-2018
            pattern = re.compile("^statistics-[0-9]{4}$")

            if not pattern.match(core):
                continue

            # Append current core to list
            statistics_core_years.append(core)

    # Initialize a string to hold our shards (may end up being empty if the Solr
    # core has not been processed by stats-util).
    shards = str()

    if len(statistics_core_years) > 0:
        # Begin building a string of shards starting with the default one
        shards = f"{SOLR_SERVER}/statistics"

        for core in statistics_core_years:
            # Create a comma-separated list of shards to pass to our Solr query
            #
            # See: https://wiki.apache.org/solr/DistributedSearch
            shards += f",{SOLR_SERVER}/{core}"

    # Return the string of shards, which may actually be empty. Solr doesn't
    # seem to mind if the shards query parameter is empty and I haven't seen
    # any negative performance impact so this should be fine.
    return shards


def is_valid_date(date):
    try:
        # Solr date format is: 2020-01-01T00:00:00Z
        # See: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

        return True
    except ValueError:
        raise falcon.HTTPBadRequest(
            title="Invalid parameter",
            description=f"Invalid date format: {date}. The value must be in format: 2020-01-01T00:00:00Z.",
        )


def validate_post_parameters(req, resp, resource, params):
    """Check the POSTed request parameters for the `/items`, `/communities` and
    `/collections` endpoints.

    Meant to be used as a `before` hook.
    """

    # Only attempt to read the POSTed request if its length is not 0 (or
    # rather, in the Python sense, if length is not a False-y value).
    if req.content_length:
        doc = json.load(req.bounded_stream)
    else:
        raise falcon.HTTPBadRequest(
            title="Invalid request", description="Request body is empty."
        )

    # Parse date parameters from request body (will raise an HTTPBadRequest
    # from is_valid_date() if any parameters are invalid)
    if "dateFrom" in doc and is_valid_date(doc["dateFrom"]):
        req.context.dateFrom = doc["dateFrom"]
    else:
        req.context.dateFrom = None

    if "dateTo" in doc and is_valid_date(doc["dateTo"]):
        req.context.dateTo = doc["dateTo"]
    else:
        req.context.dateTo = None

    # Parse the limit parameter from the POST request body
    if "limit" in doc:
        if isinstance(doc["limit"], int) and 0 < doc["limit"] <= 100:
            req.context.limit = doc["limit"]
        else:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description='The "limit" parameter is invalid. The value must be an integer between 1 and 100.',
            )
    else:
        req.context.limit = 100

    # Parse the page parameter from the POST request body
    if "page" in doc:
        if isinstance(doc["page"], int) and doc["page"] >= 0:
            req.context.page = doc["page"]
        else:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description='The "page" parameter is invalid. The value must be at least 0.',
            )
    else:
        req.context.page = 0

    # Parse the list of elements from the POST request body
    if req.context.statistics_scope in doc:
        if (
            isinstance(doc[req.context.statistics_scope], list)
            and len(doc[req.context.statistics_scope]) > 0
        ):
            req.context.elements = doc[req.context.statistics_scope]
        else:
            raise falcon.HTTPBadRequest(
                title="Invalid parameter",
                description=f'The "{req.context.statistics_scope}" parameter is invalid. The value must be a comma-separated list of UUIDs.',
            )
    else:
        req.context.elements = list()


def set_statistics_scope(req, resp, resource, params):
    """Set the statistics scope (item, collection, or community) of the request
    as well as the appropriate database (for GET requests) and Solr facet fields
    (for POST requests).

    Meant to be used as a `before` hook.
    """

    # Extract the scope from the request path. This is *guaranteed* to be one
    # of the following values because we only send requests matching these few
    # patterns to routes using this set_statistics_scope hook.
    #
    # Note: this regex is ordered so that "items" and "collections" match before
    # "item" and "collection".
    req.context.statistics_scope = re.findall(
        r"^/(communities|community|collections|collection|items|item)", req.path
    )[0]

    # Set the correct database based on the statistics_scope. The database is
    # used for all GET requests where statistics are returned directly from the
    # database. In this case we can return early.
    if req.method == "GET":
        if re.findall(r"^(item|items)$", req.context.statistics_scope):
            req.context.database = "items"
        elif re.findall(r"^(community|communities)$", req.context.statistics_scope):
            req.context.database = "communities"
        elif re.findall(r"^(collection|collections)$", req.context.statistics_scope):
            req.context.database = "collections"

        # GET requests only need the scope and the database so we can return now
        return

    # If the current request is for a plural items, communities, or collections
    # that includes a list of element ids POSTed with the request body then we
    # need to set the Solr facet field so we can get the live results.
    if req.method == "POST":
        if req.context.statistics_scope == "items":
            req.context.views_facet_field = "id"
            req.context.downloads_facet_field = "owningItem"
        elif req.context.statistics_scope == "communities":
            req.context.views_facet_field = "owningComm"
            req.context.downloads_facet_field = "owningComm"
        elif req.context.statistics_scope == "collections":
            req.context.views_facet_field = "owningColl"
            req.context.downloads_facet_field = "owningColl"


# vim: set sw=4 ts=4 expandtab:
