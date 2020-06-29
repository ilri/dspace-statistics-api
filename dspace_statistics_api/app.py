import falcon
import re
import requests
from .config import SOLR_SERVER
from datetime import datetime, timedelta, date


# Enumerate the cores in Solr to determine if statistics have been sharded into
# yearly shards by DSpace's stats-util or not (for example: statistics-2018).
def get_statistics_shards():
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
        shards = "{}/statistics".format(SOLR_SERVER)

        for core in statistics_core_years:
            # Create a comma-separated list of shards to pass to our Solr query
            #
            # See: https://wiki.apache.org/solr/DistributedSearch
            shards += ",{}/{}".format(SOLR_SERVER, core)

    # Return the string of shards, which may actually be empty. Solr doesn't
    # seem to mind if the shards query parameter is empty and I haven't seen
    # any negative performance impact so this should be fine.
    return shards


class RootResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        with open("dspace_statistics_api/docs/index.html", "r") as f:
            resp.body = f.read()


class AllItemsResource:
    def on_get(self, req, resp, item_id=0):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        start_date = req.get_param_as_date("start_date") or None
        end_date = req.get_param_as_date("end_date") or date.today()
        limit = req.get_param_as_int("limit", min_value=0, max_value=100) or 100
        page = req.get_param_as_int("page", min_value=0) or 0
        aggregate = req.get_param("aggregate") or ""
        if aggregate != "country" and aggregate != "city":
            aggregate = ""

        # Define common query params
        main_solr_query_params = {
            "facet": "true",
            "facet.mincount": 1,
            "shards": get_statistics_shards(),
            "rows": 0,
            "wt": "json",
            "json.nl": "map"  # return facets as a dict instead of a flat list
        }
        # Define common views query params
        main_solr_views_query_params = main_solr_query_params.copy()
        main_solr_views_query_params.update({
            "q": "type:2",
            "fq": "isBot:false AND statistics_type:view"
        })
        # Define common downloads query params
        main_solr_downloads_query_params = main_solr_query_params.copy()
        main_solr_downloads_query_params.update({
            "q": "type:0",
            "fq": "isBot:false AND statistics_type:view AND bundleName:ORIGINAL",
        })

        if item_id > 0:
            main_solr_views_query_params.update({"q": "type:2 AND id:" + str(item_id)})
            main_solr_downloads_query_params.update({"q": "type:0 AND owningItem:" + str(item_id)})

        if start_date is not None:
            # As the statistics will be returned by month, the period should start from the first day of the month
            # from `start_date` and end with the last day of the month `end_date`

            # Set `start_date` to the first day in the month
            start_date = start_date.replace(day=1)

            # Set `end_date` to the next month
            end_date = end_date.replace(month=end_date.month + 1)
            # Set `end_date` to the last day of the previous month
            end_date = end_date.replace(day=1) - timedelta(days=1)

            if start_date > end_date:
                temp_start_date = start_date
                start_date = end_date
                end_date = temp_start_date

            # Convert `start_date` to solr date format
            start_date = start_date.strftime("%Y-%m-%d") + "T00:00:00Z"
            # Convert `end_date` to solr date format
            end_date = end_date.strftime("%Y-%m-%d") + "T00:00:00Z"

            main_solr_views_query_params.update({
                "facet.range": "time",
                "facet.range.end": end_date,
                "facet.range.gap": "+1MONTH",
                "facet.range.start": start_date
            })
            main_solr_downloads_query_params.update({
                "facet.range": "time",
                "facet.range.end": end_date,
                "facet.range.gap": "+1MONTH",
                "facet.range.start": start_date
            })

        solr_url = SOLR_SERVER + "/statistics/select"

        solr_query_params = main_solr_views_query_params.copy()
        solr_query_params.update({
            "facet.field": "id",
            "facet.limit": 1,
            "facet.offset": 0,
            "stats": "true",
            "stats.field": "id",
            "stats.calcdistinct": "true"
        })
        res = requests.get(solr_url, params=solr_query_params)
        try:
            # get total number of distinct facets (countDistinct)
            results_total_num_facets = res.json()["stats"]["stats_fields"]["id"]["countDistinct"]
            # divide results into "pages" (cast to int to effectively round down)
            total_pages = int(results_total_num_facets / limit)
            if item_id > 0:
                page = total_pages

            if page > total_pages:
                resp.media = {
                    "current_page": page,
                    "total_pages": total_pages,
                    "limit": limit,
                    "statistics": [],
                }
            else:
                statistics = resp.media = get_counts(limit, page * limit, aggregate == "country", aggregate == "city",
                                                     main_solr_views_query_params, main_solr_downloads_query_params)
                if item_id > 0:
                    resp.media = statistics
                else:
                    response = {
                        "current_page": page,
                        "total_pages": total_pages,
                        "limit": limit
                    }
                    response.update(statistics)
                    resp.media = response
        except TypeError:
            if item_id > 0:
                resp.media = []
            else:
                resp.media = {
                    "current_page": 0,
                    "total_pages": 0,
                    "limit": 0,
                    "statistics": [],
                }


def get_counts(limit, offset, aggregate_country, aggregate_city, main_solr_views_query_params,
               main_solr_downloads_query_params):
    solr_url = SOLR_SERVER + "/statistics/select"

    # Define the dict to fill statistics
    data = {}

    ##
    ## Views
    ##
    if aggregate_country:
        facet_pivot = "id,countryCode"
    elif aggregate_city:
        facet_pivot = "id,city"
    else:
        facet_pivot = "id"
    solr_query_params = main_solr_views_query_params.copy()
    solr_query_params.update({
        "facet.pivot": facet_pivot,
        "f.id.facet.limit": limit,
        "f.id.facet.offset": offset,
    })
    res = requests.get(solr_url, params=solr_query_params)
    # Solr returns facets as a dict of dicts (see json.nl parameter)
    result = res.json()["facet_counts"]
    views = result["facet_pivot"][facet_pivot]

    total_views_by_month = None
    if "time" in result["facet_ranges"]:
        total_views_by_month = {}
        for time, count in result["facet_ranges"]["time"]["counts"].items():
            date = time.split("-")
            date = date[0] + '-' + date[1]
            total_views_by_month[date] = count

    for item in views:
        item_id = item["value"]
        if not item_id in data:
            data[item_id] = {"item_id": item_id, "views": 0, "downloads": 0}
            if aggregate_country:
                data[item_id]["countries"] = {}
            if aggregate_city:
                data[item_id]["cities"] = {}
        data[item_id]["views"] = item["count"]
        if aggregate_country and "pivot" in item:
            for country in item["pivot"]:
                country_iso = country["value"]
                if not country_iso in data[item_id]["countries"]:
                    data[item_id]["countries"][country_iso] = {"country_iso": country_iso, "views": 0, "downloads": 0}
                data[item_id]["countries"][country_iso]["views"] = country["count"]

        if aggregate_city and "pivot" in item:
            for city in item["pivot"]:
                city_name = city["value"]
                if not city_name in data[item_id]["cities"]:
                    data[item_id]["cities"][city_name] = {"city_name": city_name, "views": 0, "downloads": 0}
                data[item_id]["cities"][city_name]["views"] = city["count"]

    ##
    ## Downloads
    ##
    if aggregate_country:
        facet_pivot = "owningItem,countryCode"
    elif aggregate_city:
        facet_pivot = "owningItem,city"
    else:
        facet_pivot = "owningItem"
    solr_query_params = main_solr_downloads_query_params.copy()
    solr_query_params.update({
        "facet.pivot": facet_pivot,
        "f.owningItem.facet.limit": limit,
        "f.owningItem.facet.offset": offset,
    })
    res = requests.get(solr_url, params=solr_query_params)
    # Solr returns facets as a dict of dicts (see json.nl parameter)
    result = res.json()["facet_counts"]
    downloads = result["facet_pivot"][facet_pivot]
    total_downloads_by_month = None
    if "time" in result["facet_ranges"]:
        total_downloads_by_month = {}
        for time, count in result["facet_ranges"]["time"]["counts"].items():
            date = time.split("-")
            date = date[0] + '-' + date[1]
            total_downloads_by_month[date] = count

    for item in downloads:
        item_id = item["value"]
        if not item_id in data:
            data[item_id] = {"item_id": item_id, "views": 0, "downloads": 0}
            if aggregate_country:
                data[item_id]["countries"] = {}
            if aggregate_city:
                data[item_id]["cities"] = {}
        data[item_id]["downloads"] = item["count"]

        if aggregate_country and "pivot" in item:
            for country in item["pivot"]:
                country_iso = country["value"]
                if not country_iso in data[item_id]["countries"]:
                    data[item_id]["countries"][country_iso] = {"country_iso": country_iso, "views": 0, "downloads": 0}
                data[item_id]["countries"][country_iso]["downloads"] = country["count"]
        if aggregate_city and "pivot" in item:
            for city in item["pivot"]:
                city_name = city["value"]
                if not city_name in data[item_id]["cities"]:
                    data[item_id]["cities"][city_name] = {"city_name": city_name, "views": 0, "downloads": 0}
                data[item_id]["cities"][city_name]["downloads"] = city["count"]

    final_data = []
    for item_id, info in data.items():
        if "countries" in info:
            info["countries"] = [v for k, v in info["countries"].items()]
        if "cities" in info:
            info["cities"] = [v for k, v in info["cities"].items()]
        final_data.append(info)

    final_data = {"statistics": final_data}

    if total_views_by_month is not None or total_downloads_by_month is not None:
        if total_views_by_month is not None:
            final_data["total_views_by_month"] = total_views_by_month
        if total_downloads_by_month is not None:
            final_data["total_downloads_by_month"] = total_downloads_by_month
    return final_data


api = application = falcon.API()
api.add_route("/", RootResource())
api.add_route("/items", AllItemsResource())
api.add_route("/items/{item_id:int}", AllItemsResource())

# vim: set sw=4 ts=4 expandtab:

