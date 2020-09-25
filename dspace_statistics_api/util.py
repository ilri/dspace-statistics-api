def get_statistics_shards():
    """Enumerate the cores in Solr to determine if statistics have been sharded into
    yearly shards by DSpace's stats-util or not (for example: statistics-2018).

    Returns:
        str:A list of Solr statistics shards separated by commas.
    """
    from .config import SOLR_SERVER

    import re
    import requests

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
    import datetime
    import falcon

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
