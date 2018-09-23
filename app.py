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
        # get item views (and catch the TypeError if item doesn't have any views)
        cursor.execute('SELECT views FROM itemviews WHERE id={0}'.format(item_id))
        try:
            views = cursor.fetchone()['views']
        except:
            views = 0

        # get item downloads (and catch the TypeError if item doesn't have any downloads)
        cursor.execute('SELECT downloads FROM itemdownloads WHERE id={0}'.format(item_id))
        try:
            downloads = cursor.fetchone()['downloads']
        except:
            downloads = 0

        cursor.close()

        statistics = {
            'id': item_id,
            'views': views,
            'downloads': downloads
        }

        resp.media = statistics

api = falcon.API()
api.add_route('/item/{item_id:int}', ItemResource())

# vim: set sw=4 ts=4 expandtab:
