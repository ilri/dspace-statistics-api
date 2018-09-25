#!/usr/bin/env python
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

from database import database_connection
from solr import solr_connection

def index_views():
    print("Populating database with item views.")

    # determine the total number of items with views (aka Solr's numFound)
    res = solr.query('statistics', {
        'q':'type:2',
        'fq':'isBot:false AND statistics_type:view',
        'facet':True,
        'facet.field':'id',
    }, rows=0)

    # divide results into "pages" (numFound / 100)
    results_numFound = res.get_num_found()
    results_per_page = 100
    results_num_pages = round(results_numFound / results_per_page)
    results_current_page = 0

    cursor = db.cursor()

    while results_current_page <= results_num_pages:
        print('Page {} of {}.'.format(results_current_page, results_num_pages))

        res = solr.query('statistics', {
            'q':'type:2',
            'fq':'isBot:false AND statistics_type:view',
            'facet':True,
            'facet.field':'id',
            'facet.limit':results_per_page,
            'facet.offset':results_current_page * results_per_page
        })

        # make sure total number of results > 0
        if res.get_num_found() > 0:
            # SolrClient's get_facets() returns a dict of dicts
            views = res.get_facets()
            # in this case iterate over the 'id' dict and get the item ids and views
            for item_id, item_views in views['id'].items():
                cursor.execute('''INSERT INTO items(id, views) VALUES(%s, %s)
                               ON CONFLICT(id) DO UPDATE SET downloads=excluded.views''',
                               (item_id, item_views))

        db.commit()

        results_current_page += 1

    cursor.close()

def index_downloads():
    print("Populating database with item downloads.")

    # determine the total number of items with downloads (aka Solr's numFound)
    res = solr.query('statistics', {
        'q':'type:0',
        'fq':'isBot:false AND statistics_type:view AND bundleName:ORIGINAL',
        'facet':True,
        'facet.field':'owningItem',
    }, rows=0)

    # divide results into "pages" (numFound / 100)
    results_numFound = res.get_num_found()
    results_per_page = 100
    results_num_pages = round(results_numFound / results_per_page)
    results_current_page = 0

    cursor = db.cursor()

    while results_current_page <= results_num_pages:
        print('Page {} of {}.'.format(results_current_page, results_num_pages))

        res = solr.query('statistics', {
            'q':'type:0',
            'fq':'isBot:false AND statistics_type:view AND bundleName:ORIGINAL',
            'facet':True,
            'facet.field':'owningItem',
            'facet.limit':results_per_page,
            'facet.offset':results_current_page * results_per_page
        })

        # make sure total number of results > 0
        if res.get_num_found() > 0:
            # SolrClient's get_facets() returns a dict of dicts
            downloads = res.get_facets()
            # in this case iterate over the 'owningItem' dict and get the item ids and downloads
            for item_id, item_downloads in downloads['owningItem'].items():
                cursor.execute('''INSERT INTO items(id, downloads) VALUES(%s, %s)
                               ON CONFLICT(id) DO UPDATE SET downloads=excluded.downloads''',
                               (item_id, item_downloads))

        db.commit()

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
