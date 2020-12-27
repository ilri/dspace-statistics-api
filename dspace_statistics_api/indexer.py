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
# Connects to a DSpace Solr statistics core and ingests views and downloads for
# communities, collections, and items into a PostgreSQL database.
#
# This script is written for Python 3.6+ and requires several modules that you
# can install with pip (I recommend using a Python virtual environment):
#
#   $ pip install psycopg2-binary
#
# See: https://wiki.duraspace.org/display/DSPACE/Solr

import math

import psycopg2.extras
import requests

from .config import SOLR_SERVER
from .database import DatabaseManager
from .util import get_statistics_shards


def index_views(indexType: str, facetField: str):
    # get total number of distinct facets for items with a minimum of 1 view,
    # otherwise Solr returns all kinds of weird ids that are actually not in
    # the database. Also, stats are expensive, but we need stats.calcdistinct
    # so we can get the countDistinct summary to calculate how many pages of
    # results we have.
    #
    # see: https://lucene.apache.org/solr/guide/6_6/the-stats-component.html
    solr_query_params = {
        "q": "type:2",
        "fq": "-isBot:true AND statistics_type:view",
        "fl": facetField,
        "facet": "true",
        "facet.field": facetField,
        "facet.mincount": 1,
        "facet.limit": 1,
        "facet.offset": 0,
        "stats": "true",
        "stats.field": facetField,
        "stats.calcdistinct": "true",
        "shards": shards,
        "rows": 0,
        "wt": "json",
    }

    solr_url = SOLR_SERVER + "/statistics/select"

    res = requests.get(solr_url, params=solr_query_params)

    try:
        # get total number of distinct facets (countDistinct)
        results_totalNumFacets = res.json()["stats"]["stats_fields"][facetField][
            "countDistinct"
        ]
    except TypeError:
        print(f"{indexType}: no views, exiting.")

        exit(0)

    # divide results into "pages" and round up to next integer
    results_per_page = 100
    results_num_pages = math.ceil(results_totalNumFacets / results_per_page)
    results_current_page = 0

    with DatabaseManager() as db:
        with db.cursor() as cursor:
            # create an empty list to store values for batch insertion
            data = []

            while results_current_page <= results_num_pages:
                # "pages" are zero based, but one based is more human readable
                print(
                    f"{indexType}: indexing views (page {results_current_page + 1} of {results_num_pages + 1})"
                )

                solr_query_params = {
                    "q": "type:2",
                    "fq": "-isBot:true AND statistics_type:view",
                    "fl": facetField,
                    "facet": "true",
                    "facet.field": facetField,
                    "facet.mincount": 1,
                    "facet.limit": results_per_page,
                    "facet.offset": results_current_page * results_per_page,
                    "shards": shards,
                    "rows": 0,
                    "wt": "json",
                    "json.nl": "map",  # return facets as a dict instead of a flat list
                }

                res = requests.get(solr_url, params=solr_query_params)

                # Solr returns facets as a dict of dicts (see json.nl parameter)
                views = res.json()["facet_counts"]["facet_fields"]
                # iterate over the facetField dict and get the ids and views
                for id_, views in views[facetField].items():
                    data.append((id_, views))

                # do a batch insert of values from the current "page" of results
                sql = f"INSERT INTO {indexType}(id, views) VALUES %s ON CONFLICT(id) DO UPDATE SET views=excluded.views"
                psycopg2.extras.execute_values(cursor, sql, data, template="(%s, %s)")
                db.commit()

                # clear all items from the list so we can populate it with the next batch
                data.clear()

                results_current_page += 1


def index_downloads(indexType: str, facetField: str):
    # get the total number of distinct facets for items with at least 1 download
    solr_query_params = {
        "q": "type:0",
        "fq": "-isBot:true AND statistics_type:view AND bundleName:ORIGINAL",
        "fl": facetField,
        "facet": "true",
        "facet.field": facetField,
        "facet.mincount": 1,
        "facet.limit": 1,
        "facet.offset": 0,
        "stats": "true",
        "stats.field": facetField,
        "stats.calcdistinct": "true",
        "shards": shards,
        "rows": 0,
        "wt": "json",
    }

    solr_url = SOLR_SERVER + "/statistics/select"

    res = requests.get(solr_url, params=solr_query_params)

    try:
        # get total number of distinct facets (countDistinct)
        results_totalNumFacets = res.json()["stats"]["stats_fields"][facetField][
            "countDistinct"
        ]
    except TypeError:
        print(f"{indexType}: no downloads, exiting.")

        exit(0)

    results_per_page = 100
    results_num_pages = math.ceil(results_totalNumFacets / results_per_page)
    results_current_page = 0

    with DatabaseManager() as db:
        with db.cursor() as cursor:
            # create an empty list to store values for batch insertion
            data = []

            while results_current_page <= results_num_pages:
                # "pages" are zero based, but one based is more human readable
                print(
                    f"{indexType}: indexing downloads (page {results_current_page + 1} of {results_num_pages + 1})"
                )

                solr_query_params = {
                    "q": "type:0",
                    "fq": "-isBot:true AND statistics_type:view AND bundleName:ORIGINAL",
                    "fl": facetField,
                    "facet": "true",
                    "facet.field": facetField,
                    "facet.mincount": 1,
                    "facet.limit": results_per_page,
                    "facet.offset": results_current_page * results_per_page,
                    "shards": shards,
                    "rows": 0,
                    "wt": "json",
                    "json.nl": "map",  # return facets as a dict instead of a flat list
                }

                res = requests.get(solr_url, params=solr_query_params)

                # Solr returns facets as a dict of dicts (see json.nl parameter)
                downloads = res.json()["facet_counts"]["facet_fields"]
                # iterate over the facetField dict and get the item ids and downloads
                for id_, downloads in downloads[facetField].items():
                    data.append((id_, downloads))

                # do a batch insert of values from the current "page" of results
                sql = f"INSERT INTO {indexType}(id, downloads) VALUES %s ON CONFLICT(id) DO UPDATE SET downloads=excluded.downloads"
                psycopg2.extras.execute_values(cursor, sql, data, template="(%s, %s)")
                db.commit()

                # clear all items from the list so we can populate it with the next batch
                data.clear()

                results_current_page += 1


with DatabaseManager() as db:
    with db.cursor() as cursor:
        # create table to store item views and downloads
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS items
                  (id UUID PRIMARY KEY, views INT DEFAULT 0, downloads INT DEFAULT 0)"""
        )
        # create table to store community views and downloads
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS communities
                  (id UUID PRIMARY KEY, views INT DEFAULT 0, downloads INT DEFAULT 0)"""
        )
        # create table to store collection views and downloads
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS collections
                  (id UUID PRIMARY KEY, views INT DEFAULT 0, downloads INT DEFAULT 0)"""
        )

    # commit the table creation before closing the database connection
    db.commit()

shards = get_statistics_shards()

# Index views and downloads for items, communities, and collections. Here the
# first parameter is the type of indexing to perform, and the second parameter
# is the field to facet by in Solr's statistics to get this information.

index_views("items", "id")
index_views("communities", "owningComm")
index_views("collections", "owningColl")

index_downloads("items", "owningItem")
index_downloads("communities", "owningComm")
index_downloads("collections", "owningColl")

# vim: set sw=4 ts=4 expandtab:
