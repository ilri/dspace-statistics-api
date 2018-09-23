#!/usr/bin/env python
#
# Tested with Python 3.6
# See DSpace Solr docs for tips about parameters
# https://wiki.duraspace.org/display/DSPACE/Solr

from config import SOLR_CORE
from database import database_connection
from solr import solr_connection

def index_views():
    print("Populating database with item views.")

    # determine the total number of items with views (aka Solr's numFound)
    res = solr.query(SOLR_CORE, {
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

    while results_current_page <= results_num_pages:
        print('Page {0} of {1}.'.format(results_current_page, results_num_pages))

        res = solr.query(SOLR_CORE, {
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
                db.execute('''REPLACE INTO itemviews VALUES (?, ?)''', (item_id, item_views))

        db.commit()

        results_current_page += 1

def index_downloads():
    print("Populating database with item downloads.")

    # determine the total number of items with downloads (aka Solr's numFound)
    res = solr.query(SOLR_CORE, {
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

    while results_current_page <= results_num_pages:
        print('Page {0} of {1}.'.format(results_current_page, results_num_pages))

        res = solr.query(SOLR_CORE, {
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
                db.execute('''REPLACE INTO itemdownloads VALUES (?, ?)''', (item_id, item_downloads))

        db.commit()

        results_current_page += 1

db = database_connection()
solr = solr_connection()

# use separate views and downloads tables so we can REPLACE INTO carelessly (ie, item may have views but no downloads)
db.execute('''CREATE TABLE IF NOT EXISTS itemviews
                  (id integer primary key, views integer)''')
db.execute('''CREATE TABLE IF NOT EXISTS itemdownloads
                  (id integer primary key, downloads integer)''')
index_views()
index_downloads()

db.close()

# vim: set sw=4 ts=4 expandtab:
