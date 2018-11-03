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

from .database import database_connection
import json
import psycopg2.extras
from .solr import solr_connection


def index_views():
    # get total number of distinct facets for items with a minimum of 1 view,
    # otherwise Solr returns all kinds of weird ids that are actually not in
    # the database. Also, stats are expensive, but we need stats.calcdistinct
    # so we can get the countDistinct summary.
    #
    # see: https://lucene.apache.org/solr/guide/6_6/the-stats-component.html
    res = solr.query('statistics', {
        'q': 'type:2',
        'fq': 'isBot:false AND statistics_type:view',
        'facet': True,
        'facet.field': 'id',
        'facet.mincount': 1,
        'facet.limit': 1,
        'facet.offset': 0,
        'stats': True,
        'stats.field': 'id',
        'stats.calcdistinct': True
    }, rows=0)

    # get total number of distinct facets (countDistinct)
    results_totalNumFacets = json.loads(res.get_json())['stats']['stats_fields']['id']['countDistinct']

    # divide results into "pages" (cast to int to effectively round down)
    results_per_page = 100
    results_num_pages = int(results_totalNumFacets / results_per_page)
    results_current_page = 0

    cursor = db.cursor()

    # create an empty list to store values for batch insertion
    data = []

    while results_current_page <= results_num_pages:
        print('Indexing item views (page {} of {})'.format(results_current_page, results_num_pages))

        res = solr.query('statistics', {
            'q': 'type:2',
            'fq': 'isBot:false AND statistics_type:view',
            'facet': True,
            'facet.field': 'id',
            'facet.mincount': 1,
            'facet.limit': results_per_page,
            'facet.offset': results_current_page * results_per_page
        }, rows=0)

        # SolrClient's get_facets() returns a dict of dicts
        views = res.get_facets()
        # in this case iterate over the 'id' dict and get the item ids and views
        for item_id, item_views in views['id'].items():
            data.append((item_id, item_views))

        # do a batch insert of values from the current "page" of results
        sql = 'INSERT INTO items(id, views) VALUES %s ON CONFLICT(id) DO UPDATE SET views=excluded.views'
        psycopg2.extras.execute_values(cursor, sql, data, template='(%s, %s)')
        db.commit()

        # clear all items from the list so we can populate it with the next batch
        data.clear()

        results_current_page += 1

    cursor.close()


def index_downloads():
    # get the total number of distinct facets for items with at least 1 download
    res = solr.query('statistics', {
        'q': 'type:0',
        'fq': 'isBot:false AND statistics_type:view AND bundleName:ORIGINAL',
        'facet': True,
        'facet.field': 'owningItem',
        'facet.mincount': 1,
        'facet.limit': 1,
        'facet.offset': 0,
        'stats': True,
        'stats.field': 'owningItem',
        'stats.calcdistinct': True
    }, rows=0)

    # get total number of distinct facets (countDistinct)
    results_totalNumFacets = json.loads(res.get_json())['stats']['stats_fields']['owningItem']['countDistinct']

    # divide results into "pages" (cast to int to effectively round down)
    results_per_page = 100
    results_num_pages = int(results_totalNumFacets / results_per_page)
    results_current_page = 0

    cursor = db.cursor()

    # create an empty list to store values for batch insertion
    data = []

    while results_current_page <= results_num_pages:
        print('Indexing item downloads (page {} of {})'.format(results_current_page, results_num_pages))

        res = solr.query('statistics', {
            'q': 'type:0',
            'fq': 'isBot:false AND statistics_type:view AND bundleName:ORIGINAL',
            'facet': True,
            'facet.field': 'owningItem',
            'facet.mincount': 1,
            'facet.limit': results_per_page,
            'facet.offset': results_current_page * results_per_page
        }, rows=0)

        # SolrClient's get_facets() returns a dict of dicts
        downloads = res.get_facets()
        # in this case iterate over the 'owningItem' dict and get the item ids and downloads
        for item_id, item_downloads in downloads['owningItem'].items():
            data.append((item_id, item_downloads))

        # do a batch insert of values from the current "page" of results
        sql = 'INSERT INTO items(id, downloads) VALUES %s ON CONFLICT(id) DO UPDATE SET downloads=excluded.downloads'
        psycopg2.extras.execute_values(cursor, sql, data, template='(%s, %s)')
        db.commit()

        # clear all items from the list so we can populate it with the next batch
        data.clear()

        results_current_page += 1

    cursor.close()


db = database_connection()
solr = solr_connection()

# create table to store item views and downloads
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS items
                  (id INT PRIMARY KEY, views INT DEFAULT 0, downloads INT DEFAULT 0)''')
index_views()
index_downloads()

db.close()

# vim: set sw=4 ts=4 expandtab:
