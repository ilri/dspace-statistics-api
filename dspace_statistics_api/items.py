import requests

from .config import SOLR_SERVER
from .util import get_statistics_shards


def get_views(solr_date_string: str, items: list):
    """
    Get view statistics for a list of items from Solr.

    :parameter solr_date_string (str): Solr date string, for example "[* TO *]"
    :parameter items (list): a list of item IDs
    :returns: A dict of item IDs and views
    """
    # Join the UUIDs with "OR" and escape the hyphens for Solr
    solr_items_string: str = " OR ".join(items).replace("-", r"\-")

    solr_query_params = {
        "q": f"id:({solr_items_string})",
        "fq": f"type:2 AND isBot:false AND statistics_type:view AND time:{solr_date_string}",
        "facet": "true",
        "facet.field": "id",
        "facet.mincount": 1,
        "shards": shards,
        "rows": 0,
        "wt": "json",
        "json.nl": "map",  # return facets as a dict instead of a flat list
    }

    solr_url = SOLR_SERVER + "/statistics/select"
    res = requests.get(solr_url, params=solr_query_params)

    # Create an empty dict to store views
    data = {}

    # Solr returns facets as a dict of dicts (see the json.nl parameter)
    views = res.json()["facet_counts"]["facet_fields"]
    # iterate over the 'id' dict and get the item ids and views
    for item_id, item_views in views["id"].items():
        data[item_id] = item_views

    # Check if any items have missing stats so we can set them to 0
    if len(data) < len(items):
        # List comprehension to get a list of item ids (keys) in the data
        data_ids = [k for k, v in data.items()]
        for item_id in items:
            if item_id not in data_ids:
                data[item_id] = 0
                continue

    return data


def get_downloads(solr_date_string: str, items: list):
    """
    Get download statistics for a list of items from Solr.

    :parameter solr_date_string (str): Solr date string, for example "[* TO *]"
    :parameter items (list): a list of item IDs
    :returns: A dict of item IDs and downloads
    """
    # Join the UUIDs with "OR" and escape the hyphens for Solr
    solr_items_string: str = " OR ".join(items).replace("-", r"\-")

    solr_query_params = {
        "q": f"owningItem:({solr_items_string})",
        "fq": f"type:0 AND isBot:false AND statistics_type:view AND bundleName:ORIGINAL AND time:{solr_date_string}",
        "facet": "true",
        "facet.field": "owningItem",
        "facet.mincount": 1,
        "shards": shards,
        "rows": 0,
        "wt": "json",
        "json.nl": "map",  # return facets as a dict instead of a flat list
    }

    solr_url = SOLR_SERVER + "/statistics/select"
    res = requests.get(solr_url, params=solr_query_params)

    # Create an empty dict to store downloads
    data = {}

    # Solr returns facets as a dict of dicts (see the json.nl parameter)
    downloads = res.json()["facet_counts"]["facet_fields"]
    # Iterate over the 'owningItem' dict and get the item ids and downloads
    for item_id, item_downloads in downloads["owningItem"].items():
        data[item_id] = item_downloads

    # Check if any items have missing stats so we can set them to 0
    if len(data) < len(items):
        # List comprehension to get a list of item ids (keys) in the data
        data_ids = [k for k, v in data.items()]
        for item_id in items:
            if item_id not in data_ids:
                data[item_id] = 0
                continue

    return data


shards = get_statistics_shards()

# vim: set sw=4 ts=4 expandtab:
