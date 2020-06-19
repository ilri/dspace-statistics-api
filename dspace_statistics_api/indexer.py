#
# indexer.py
#
# Copyright 2018 Alan Orth.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---
#
# Connects to a DSpace Solr statistics core and ingests item views and downloads
# into a PostgreSQL database for use by other applications (like an API).
#
# This script is written for Python 3.5+ and requires several modules that you
# can install with pip (I recommend using a Python virtual environment):
#
#   $ pip install SolrClient psycopg2-binary
#
# See: https://solrclient.readthedocs.io/en/latest/SolrClient.html
# See: https://wiki.duraspace.org/display/DSPACE/Solr

import re

import psycopg2.extras
import requests

from .config import SOLR_SERVER
from .database import DatabaseManager


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


def index_views():
    # get total number of distinct facets for items with a minimum of 1 view,
    # otherwise Solr returns all kinds of weird ids that are actually not in
    # the database. Also, stats are expensive, but we need stats.calcdistinct
    # so we can get the countDistinct summary.
    #
    # see: https://lucene.apache.org/solr/guide/6_6/the-stats-component.html
    solr_query_params = {
        "q": "type:2",
        "fq": "isBot:false AND statistics_type:view",
        "facet": "true",
        "facet.field": "id",
        "facet.mincount": 1,
        "facet.limit": 1,
        "facet.offset": 0,
        "stats": "true",
        "stats.field": "id",
        "stats.calcdistinct": "true",
        "shards": shards,
        "rows": 0,
        "wt": "json",
    }

    solr_url = SOLR_SERVER + "/statistics/select"

    res = requests.get(solr_url, params=solr_query_params)

    try:
        # get total number of distinct facets (countDistinct)
        results_totalNumFacets = res.json()["stats"]["stats_fields"]["id"][
            "countDistinct"
        ]
    except TypeError:
        print("No item views to index, exiting.")

        exit(0)

    # divide results into "pages" (cast to int to effectively round down)
    results_per_page = 100
    results_num_pages = int(results_totalNumFacets / results_per_page)
    results_current_page = 0

    with DatabaseManager() as db:
        with db.cursor() as cursor:
            # create an empty list to store values for batch insertion
            data = []

            while results_current_page <= results_num_pages:
                # "pages" are zero based, but one based is more human readable
                print(
                    "Indexing item views (page {} of {})".format(
                        results_current_page + 1, results_num_pages + 1
                    )
                )

                solr_query_params = {
                    "q": "type:2",
                    "fq": "isBot:false AND statistics_type:view",
                    "facet": "true",
                    "facet.field": "id",
                    "facet.mincount": 1,
                    "facet.limit": results_per_page,
                    "facet.offset": results_current_page * results_per_page,
                    "shards": shards,
                    "rows": 0,
                    "wt": "json",
                    "json.nl": "map",  # return facets as a dict instead of a flat list
                }

                solr_url = SOLR_SERVER + "/statistics/select"

                res = requests.get(solr_url, params=solr_query_params)

                # Solr returns facets as a dict of dicts (see json.nl parameter)
                views = res.json()["facet_counts"]["facet_fields"]
                # iterate over the 'id' dict and get the item ids and views
                for item_id, item_views in views["id"].items():
                    # Create a list with the item ID and total views
                    item_row = [item_id, item_views]

                    # Prepare query to get the item last 12 months views
                    solr_query_params = {
                        "q": "type:2 AND id:" + item_id,
                        "fq": "isBot:false AND statistics_type:view",
                        "facet": "true",
                        "facet.date": "time",
                        "facet.date.end": "NOW/MONTH+1MONTH",
                        "facet.date.gap": "+1MONTH",
                        "facet.date.start": "NOW/MONTH-11MONTHS",
                        "shards": shards,
                        "rows": 0,
                        "wt": "json",
                        "json.nl": "map"  # return facets as a dict instead of a flat list
                    }
                    res = requests.get(solr_url, params=solr_query_params)
                    last_12_months = res.json()["facet_counts"]["facet_dates"]["time"]
                    for time, time_item_views in last_12_months.items():
                        # Exclude keys "start", "end" and "gap" from the response and add the views to the item list
                        if time != "start" and time != "end" and time != "gap":
                            item_row.append(time_item_views)

                    data.append(item_row)

                # do a batch insert of values from the current "page" of results
                sql = "INSERT INTO items(id, views, views_1, views_2, views_3, views_4, views_5, views_6, views_7, views_8, views_9, views_10, views_11, views_12) " \
                      "VALUES %s ON CONFLICT(id) " \
                      "DO UPDATE SET " \
                      "views=excluded.views," \
                      "views_1=excluded.views_1," \
                      "views_2=excluded.views_2," \
                      "views_3=excluded.views_3," \
                      "views_4=excluded.views_4," \
                      "views_5=excluded.views_5," \
                      "views_6=excluded.views_6," \
                      "views_7=excluded.views_7," \
                      "views_8=excluded.views_8," \
                      "views_9=excluded.views_9," \
                      "views_10=excluded.views_10," \
                      "views_11=excluded.views_11," \
                      "views_12=excluded.views_12"
                psycopg2.extras.execute_values(cursor, sql, data, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                db.commit()

                # clear all items from the list so we can populate it with the next batch
                data.clear()

                results_current_page += 1


def index_downloads():
    # get the total number of distinct facets for items with at least 1 download
    solr_query_params = {
        "q": "type:0",
        "fq": "isBot:false AND statistics_type:view AND bundleName:ORIGINAL",
        "facet": "true",
        "facet.field": "owningItem",
        "facet.mincount": 1,
        "facet.limit": 1,
        "facet.offset": 0,
        "stats": "true",
        "stats.field": "owningItem",
        "stats.calcdistinct": "true",
        "shards": shards,
        "rows": 0,
        "wt": "json",
    }

    solr_url = SOLR_SERVER + "/statistics/select"

    res = requests.get(solr_url, params=solr_query_params)

    try:
        # get total number of distinct facets (countDistinct)
        results_totalNumFacets = res.json()["stats"]["stats_fields"]["owningItem"][
            "countDistinct"
        ]
    except TypeError:
        print("No item downloads to index, exiting.")

        exit(0)

    # divide results into "pages" (cast to int to effectively round down)
    results_per_page = 100
    results_num_pages = int(results_totalNumFacets / results_per_page)
    results_current_page = 0

    with DatabaseManager() as db:
        with db.cursor() as cursor:
            # create an empty list to store values for batch insertion
            data = []

            while results_current_page <= results_num_pages:
                # "pages" are zero based, but one based is more human readable
                print(
                    "Indexing item downloads (page {} of {})".format(
                        results_current_page + 1, results_num_pages + 1
                    )
                )

                solr_query_params = {
                    "q": "type:0",
                    "fq": "isBot:false AND statistics_type:view AND bundleName:ORIGINAL",
                    "facet": "true",
                    "facet.field": "owningItem",
                    "facet.mincount": 1,
                    "facet.limit": results_per_page,
                    "facet.offset": results_current_page * results_per_page,
                    "shards": shards,
                    "rows": 0,
                    "wt": "json",
                    "json.nl": "map",  # return facets as a dict instead of a flat list
                }

                solr_url = SOLR_SERVER + "/statistics/select"

                res = requests.get(solr_url, params=solr_query_params)

                # Solr returns facets as a dict of dicts (see json.nl parameter)
                downloads = res.json()["facet_counts"]["facet_fields"]
                # iterate over the 'owningItem' dict and get the item ids and downloads
                for item_id, item_downloads in downloads["owningItem"].items():
                    # Create a list with the item ID and total views
                    item_row = [item_id, item_downloads]

                    # Prepare query to get the item last 12 months views
                    solr_query_params = {
                        "q": "type:0 AND owningItem:" + item_id,
                        "fq": "isBot:false AND statistics_type:view AND bundleName:ORIGINAL",
                        "facet": "true",
                        "facet.date": "time",
                        "facet.date.end": "NOW/MONTH+1MONTH",
                        "facet.date.gap": "+1MONTH",
                        "facet.date.start": "NOW/MONTH-11MONTHS",
                        "shards": shards,
                        "rows": 0,
                        "wt": "json",
                        "json.nl": "map"  # return facets as a dict instead of a flat list
                    }
                    res = requests.get(solr_url, params=solr_query_params)
                    last_12_months = res.json()["facet_counts"]["facet_dates"]["time"]
                    for time, time_item_downloads in last_12_months.items():
                        # Exclude keys "start", "end" and "gap" from the response and add the downloads to the item list
                        if time != "start" and time != "end" and time != "gap":
                            item_row.append(time_item_downloads)

                    data.append(item_row)

                # do a batch insert of values from the current "page" of results
                sql = "INSERT INTO items(id, downloads, downloads_1, downloads_2, downloads_3, downloads_4, downloads_5, downloads_6, downloads_7, downloads_8, downloads_9, downloads_10, downloads_11, downloads_12) " \
                      "VALUES %s ON CONFLICT(id) " \
                      "DO UPDATE SET " \
                      "downloads=excluded.downloads," \
                      "downloads_1=excluded.downloads_1," \
                      "downloads_2=excluded.downloads_2," \
                      "downloads_3=excluded.downloads_3," \
                      "downloads_4=excluded.downloads_4," \
                      "downloads_5=excluded.downloads_5," \
                      "downloads_6=excluded.downloads_6," \
                      "downloads_7=excluded.downloads_7," \
                      "downloads_8=excluded.downloads_8," \
                      "downloads_9=excluded.downloads_9," \
                      "downloads_10=excluded.downloads_10," \
                      "downloads_11=excluded.downloads_11," \
                      "downloads_12=excluded.downloads_12"
                psycopg2.extras.execute_values(cursor, sql, data, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                db.commit()

                # clear all items from the list so we can populate it with the next batch
                data.clear()

                results_current_page += 1


with DatabaseManager() as db:
    with db.cursor() as cursor:
        # create table to store item views and downloads
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS items
                  (
                  id INT PRIMARY KEY, 
                  views INT DEFAULT 0, 
                  downloads INT DEFAULT 0,
                  views_1 INT DEFAULT 0, 
                  views_2 INT DEFAULT 0, 
                  views_3 INT DEFAULT 0, 
                  views_4 INT DEFAULT 0, 
                  views_5 INT DEFAULT 0, 
                  views_6 INT DEFAULT 0, 
                  views_7 INT DEFAULT 0, 
                  views_8 INT DEFAULT 0, 
                  views_9 INT DEFAULT 0, 
                  views_10 INT DEFAULT 0, 
                  views_11 INT DEFAULT 0, 
                  views_12 INT DEFAULT 0, 
                  downloads_1 INT DEFAULT 0, 
                  downloads_2 INT DEFAULT 0, 
                  downloads_3 INT DEFAULT 0, 
                  downloads_4 INT DEFAULT 0, 
                  downloads_5 INT DEFAULT 0, 
                  downloads_6 INT DEFAULT 0, 
                  downloads_7 INT DEFAULT 0,
                  downloads_8 INT DEFAULT 0,
                  downloads_9 INT DEFAULT 0,
                  downloads_10 INT DEFAULT 0,
                  downloads_11 INT DEFAULT 0,
                  downloads_12 INT DEFAULT 0
                  );"""
        )

    # commit the table creation before closing the database connection
    db.commit()

shards = get_statistics_shards()

index_views()
index_downloads()

# vim: set sw=4 ts=4 expandtab:
