import logging

from flask import Flask, request

from core import FLASK_APP_PORT, FLASK_APP_HOST
from core.api.statistics import get_latest_stats
from core.utils.logger import init_logger
from core.utils.web import construct_ok_response
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route("/stats/")
@cross_origin(supports_credentials=True)
def get_stats():
    logger.debug(request)
    data = get_latest_stats()
    return construct_ok_response(data, pretty=True)


@app.route("/stats/<schain_name>")
@cross_origin(supports_credentials=True)
def get_schain_stats(schain_name):
    logger.debug(request)
    return construct_ok_response(None, pretty=True)


def main():
    logger.info('Starting Flask server')
    app.run(port=FLASK_APP_PORT, host=FLASK_APP_HOST)


if __name__ == '__main__':
    init_logger()
    main()
