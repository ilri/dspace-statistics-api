# Tested with Python 3.6
# See DSpace Solr docs for tips about parameters
# https://wiki.duraspace.org/display/DSPACE/Solr

from database import database_connection
import falcon
from solr import solr_connection

db = database_connection()
db.set_session(readonly=True)
solr = solr_connection()

class AllItemsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        limit = req.get_param_as_int("limit", min=0, max=100) or 100
        page = req.get_param_as_int("page", min=0) or 0
        offset = limit * page

        cursor = db.cursor()

        # get total number of items so we can estimate the pages
        cursor.execute('SELECT COUNT(id) FROM items')
        pages = round(cursor.fetchone()[0] / limit)

        # get statistics, ordered by id, and use limit and offset to page through results
        cursor.execute('SELECT id, views, downloads FROM items ORDER BY id ASC LIMIT {0} OFFSET {1}'.format(limit, offset))
        results = cursor.fetchmany(limit)
        cursor.close()

        # create a list to hold dicts of item stats
        statistics = list()

        # iterate over results and build statistics object
        for item in results:
            statistics.append({ 'id': item['id'], 'views': item['views'], 'downloads': item['downloads'] })

        message = {
                'currentPage': page,
                'totalPages': pages,
                'limit': limit,
                'statistics': statistics
        }

        resp.media = message

class ItemResource:
    def on_get(self, req, resp, item_id):
        """Handles GET requests"""

        cursor = db.cursor()
        cursor.execute('SELECT views, downloads FROM items WHERE id={0}'.format(item_id))
        results = cursor.fetchone()
        cursor.close()

        statistics = {
            'id': item_id,
            'views': results['views'],
            'downloads': results['downloads']
        }

        resp.media = statistics

api = falcon.API()
api.add_route('/', AllItemsResource())
api.add_route('/item/{item_id:int}', ItemResource())

# vim: set sw=4 ts=4 expandtab:
