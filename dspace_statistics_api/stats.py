import requests

from .config import SOLR_SERVER
from .util import get_statistics_shards


def get_views(solr_date_string: str, elements: list, facetField: str):
    """
    Get view statistics for a list of elements from Solr. Depending on the req-
    uest this could be items, communities, or collections.

    :parameter solr_date_string (str): Solr date string, for example "[* TO *]"
    :parameter elements (list): a list of IDs
    :parameter facetField (str): Solr field to facet by, for example "id"
    :returns: A dict of IDs and views
    """
    shards = get_statistics_shards()

    # Join the UUIDs with "OR" and escape the hyphens for Solr
    solr_elements_string: str = " OR ".join(elements).replace("-", r"\-")

    solr_query_params = {
        "q": f"{facetField}:({solr_elements_string})",
        "fq": f"type:2 AND -isBot:true AND statistics_type:view AND time:{solr_date_string}",
        "fl": facetField,
        "facet": "true",
        "facet.field": facetField,
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
    # iterate over the facetField dict and ids and views
    for id_, views in views[facetField].items():
        # For items we can rely on Solr returning facets for the *only* the ids
        # in our query, but for communities and collections, the owningComm and
        # owningColl fields are multi-value so Solr will return facets with the
        # values in our query as well as *any others* that happen to be present
        # in the field (which looks like Solr returning unrelated results until
        # you realize that the field is multi-value and this is correct).
        #
        # To work around this I make sure that each id in the returned dict are
        # present in the elements list POSTed by the user.
        if id_ in elements:
            data[id_] = views

    # Check if any ids have missing stats so we can set them to 0
    if len(data) < len(elements):
        # List comprehension to get a list of ids (keys) in the data
        data_ids = [k for k, v in data.items()]
        for element_id in elements:
            if element_id not in data_ids:
                data[element_id] = 0
                continue

    return data


def get_downloads(solr_date_string: str, elements: list, facetField: str):
    """
    Get download statistics for a list of items from Solr. Depending on the req-
    uest this could be items, communities, or collections.

    :parameter solr_date_string (str): Solr date string, for example "[* TO *]"
    :parameter elements (list): a list of IDs
    :parameter facetField (str): Solr field to facet by, for example "id"
    :returns: A dict of IDs and downloads
    """
    shards = get_statistics_shards()

    # Join the UUIDs with "OR" and escape the hyphens for Solr
    solr_elements_string: str = " OR ".join(elements).replace("-", r"\-")

    solr_query_params = {
        "q": f"{facetField}:({solr_elements_string})",
        "fq": f"type:0 AND -isBot:true AND statistics_type:view AND bundleName:ORIGINAL AND time:{solr_date_string}",
        "fl": facetField,
        "facet": "true",
        "facet.field": facetField,
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
    # Iterate over the facetField dict and get the ids and downloads
    for id_, downloads in downloads[facetField].items():
        # Make sure that each id in the returned dict are present in the
        # elements list POSTed by the user.
        if id_ in elements:
            data[id_] = downloads

    # Check if any elements have missing stats so we can set them to 0
    if len(data) < len(elements):
        # List comprehension to get a list of ids (keys) in the data
        data_ids = [k for k, v in data.items()]
        for element_id in elements:
            if element_id not in data_ids:
                data[element_id] = 0
                continue

    return data


# vim: set sw=4 ts=4 expandtab:
