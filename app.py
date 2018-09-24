# Tested with Python 3.6
# See DSpace Solr docs for tips about parameters
# https://wiki.duraspace.org/display/DSPACE/Solr

from database import database_connection_ro
import falcon
from solr import solr_connection

db = database_connection_ro()
solr = solr_connection()

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
api.add_route('/item/{item_id:int}', ItemResource())

# vim: set sw=4 ts=4 expandtab:
