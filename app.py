# Tested with Python 3.6
# See DSpace Solr docs for tips about parameters
# https://wiki.duraspace.org/display/DSPACE/Solr

import falcon
from SolrClient import SolrClient

solr_server = 'http://localhost:3000/solr'
solr_core = 'statistics'

class ItemResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        item_id = req.get_param_as_int("id", required=True, min=0)

        solr = SolrClient(solr_server)

        # Get views
        res = solr.query(solr_core, {
            'q':'type:0',
            'fq':'owningItem:{0} AND isBot:false AND statistics_type:view AND -bundleName:ORIGINAL'.format(item_id)
        })

        views = res.get_num_found()

        # Get downloads
        res = solr.query(solr_core, {
            'q':'type:0',
            'fq':'owningItem:{0} AND isBot:false AND statistics_type:view AND -(bundleName:[* TO *] -bundleName:ORIGINAL)'.format(item_id)
        })

        downloads = res.get_num_found() 

        statistics = {
            'id': item_id,
            'views': views,
            'downloads': downloads
        }

        resp.media = statistics

api = falcon.API()
api.add_route('/item', ItemResource())
