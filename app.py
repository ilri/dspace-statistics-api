# Tested with Python 3.6
# See DSpace Solr docs for tips about parameters
# https://wiki.duraspace.org/display/DSPACE/Solr

from config import SOLR_SERVER
from config import SOLR_CORE
import falcon
from SolrClient import SolrClient


class ItemResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        item_id = req.get_param_as_int("id", required=True, min=0)

        solr = SolrClient(SOLR_SERVER)

        # Get views
        res = solr.query(SOLR_CORE, {
            'q':'type:2 AND id:{0}'.format(item_id),
            'fq':'isBot:false AND statistics_type:view'
        }, rows=0)

        views = res.get_num_found()

        # Get downloads
        res = solr.query(SOLR_CORE, {
            'q':'type:0 AND owningItem:{0}'.format(item_id),
            'fq':'isBot:false AND statistics_type:view AND bundleName:ORIGINAL'
        }, rows=0)

        downloads = res.get_num_found() 

        statistics = {
            'id': item_id,
            'views': views,
            'downloads': downloads
        }

        resp.media = statistics

api = falcon.API()
api.add_route('/item', ItemResource())

# vim: set sw=4 ts=4 expandtab:
