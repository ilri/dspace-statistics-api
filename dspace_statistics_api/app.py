from .database import database_connection
import falcon

db = database_connection()
db.set_session(readonly=True)


class RootResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open('dspace_statistics_api/docs/index.html', 'r') as f:
            resp.body = f.read()

class AllItemsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        limit = req.get_param_as_int("limit", min=0, max=100) or 100
        page = req.get_param_as_int("page", min=0) or 0
        offset = limit * page

        cursor = db.cursor()

        # get total number of items so we can estimate the pages
        cursor.execute( 'SELECT COUNT(id) FROM items')
        pages = round(cursor.fetchone()[0] / limit)

        # get statistics, ordered by id, and use limit and offset to page through results
        cursor.execute('SELECT id, views, downloads FROM items ORDER BY id ASC LIMIT {} OFFSET {}'.format(limit, offset))

        # create a list to hold dicts of item stats
        statistics = list()

        # iterate over results and build statistics object
        for item in cursor:
            statistics.append({'id': item['id'], 'views': item['views'], 'downloads': item['downloads']})

        cursor.close()

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
        cursor.execute('SELECT views, downloads FROM items WHERE id={}'.format(item_id))
        if cursor.rowcount == 0:
            raise falcon.HTTPNotFound(
                title='Item not found',
                description='The item with id "{}" was not found.'.format(item_id)
            )
        else:
            results = cursor.fetchone()

            statistics = {
                'id': item_id,
                'views': results['views'],
                'downloads': results['downloads']
            }

            resp.media = statistics

        cursor.close()


api = application = falcon.API()
api.add_route('/', RootResource())
api.add_route('/items', AllItemsResource())
api.add_route('/item/{item_id:int}', ItemResource())

# vim: set sw=4 ts=4 expandtab:
