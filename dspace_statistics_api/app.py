import falcon

from .database import DatabaseManager
import datetime


def get_last_12_months_dates():
    # Current date
    month = datetime.date.today()
    dates = [month.strftime("%Y-%m")]

    for i in range(11):
        # Set to the 1st day in month then get the previous day (the last day in the previous month)
        month = month.replace(day=1) - datetime.timedelta(days=1)
        dates.append(month.strftime("%Y-%m"))

        # The 1st of the previous month
        month = month.replace(day=1)

    dates = list(reversed(dates))
    return dates


def get_month_date(dates, text):
    text_list = text.split("_")
    if len(text_list) == 1:
        return text
    try:
        return text_list[0] + "_" + dates[int(text_list[1]) - 1]
    except:
        return text


class RootResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        with open("dspace_statistics_api/docs/index.html", "r") as f:
            resp.body = f.read()


class AllItemsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Return HTTPBadRequest if id parameter is not present and valid
        period_range = req.get_param_as_int("period_range", min_value=0, max_value=12) or 0
        limit = req.get_param_as_int("limit", min_value=0, max_value=100) or 100
        page = req.get_param_as_int("page", min_value=0) or 0
        offset = limit * page

        columns = ["id", "views", "downloads"]
        if period_range > 0:
            for i in range(period_range):
                columns.append("views_" + str((12 - i)))
                columns.append("downloads_" + str((12 - i)))

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                # get total number of items so we can estimate the pages
                cursor.execute("SELECT COUNT(id) FROM items")
                pages = round(cursor.fetchone()[0] / limit)

                # get statistics, ordered by id, and use limit and offset to page through results
                cursor.execute(
                    "SELECT " + ", ".join(columns) + " FROM items ORDER BY id ASC LIMIT {} OFFSET {}".format(
                        limit, offset
                    )
                )

                #Get last 12 months dates
                dates = get_last_12_months_dates()

                # create a list to hold dicts of item stats
                statistics = []

                # iterate over results and build statistics object
                for item in cursor:
                    item_data = {}
                    for key, value in item.items():
                        key = get_month_date(dates, key)
                        item_data[key] = value
                    statistics.append(item_data)

        message = {
            "currentPage": page,
            "totalPages": pages,
            "limit": limit,
            "statistics": statistics,
        }

        resp.media = message


class ItemResource:
    def on_get(self, req, resp, item_id):
        """Handles GET requests"""
        period_range = req.get_param_as_int("period_range", min_value=0, max_value=12) or 0

        columns = ["id", "views", "downloads"]
        if period_range > 0:
            for i in range(period_range):
                columns.append("views_" + str((12 - i)))
                columns.append("downloads_" + str((12 - i)))

        with DatabaseManager() as db:
            db.set_session(readonly=True)

            with db.cursor() as cursor:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT " + ", ".join(columns) + " FROM items WHERE id={}".format(item_id)
                )
                if cursor.rowcount == 0:
                    raise falcon.HTTPNotFound(
                        title="Item not found",
                        description='The item with id "{}" was not found.'.format(
                            item_id
                        ),
                    )
                else:
                    result = cursor.fetchone()

                    #Get last 12 months dates
                    dates = get_last_12_months_dates()

                    statistics = {}
                    for key, value in result.items():
                        key = get_month_date(dates, key)
                        statistics[key] = value
                    resp.media = statistics


api = application = falcon.API()
api.add_route("/", RootResource())
api.add_route("/items", AllItemsResource())
api.add_route("/item/{item_id:int}", ItemResource())

# vim: set sw=4 ts=4 expandtab:
