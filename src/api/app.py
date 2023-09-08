import logging

from flask import Flask, request

from src import FLASK_APP_PORT, FLASK_APP_HOST
from src.api.ops import get_latest_stats, get_legacy_stats
from src.utils.logger import init_logger
from src.utils.web import construct_ok_response
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/v1/stats/")
@cross_origin()
def get_v1_stats():
    logger.debug(request)
    data = get_legacy_stats()
    return construct_ok_response(data, pretty=True)


@app.route("/v1/stats/<schain_name>")
@cross_origin()
def get_v1_schain_stats(schain_name):
    logger.debug(request)
    data = get_legacy_stats(schain_name)
    return construct_ok_response(data, pretty=True)


@app.route("/v2/stats/")
@cross_origin()
def get_v2_stats():
    logger.debug(request)
    data = get_latest_stats()
    return construct_ok_response(data, pretty=True)


@app.route("/v2/stats/<schain_name>")
@cross_origin()
def get_v2_schain_stats(schain_name):
    logger.debug(request)
    data = get_latest_stats(schain_name)
    return construct_ok_response(data, pretty=True)


def main():
    logger.info('Starting Flask server')
    app.run(port=FLASK_APP_PORT, host=FLASK_APP_HOST)


if __name__ == '__main__':
    init_logger()
    main()
