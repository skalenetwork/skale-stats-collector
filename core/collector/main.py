import logging
import os
from threading import Thread
from time import sleep

from core import META_DATA_PATH, ABI_FILEPATH
from core.collector.database import create_tables, refetch_daily_price_stats, get_data
from core.collector.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from core.collector.statistics import Collector, PricesCollector
from core.utils.logger import init_logger
from core.utils.meta import create_meta_file, get_meta_file, update_meta_file

logger = logging.getLogger(__name__)


def run_collectors():
    meta = get_meta_file()
    for name in meta:
        collector = Collector(name)
        Thread(target=collector.catchup_blocks, daemon=True, name=name).start()
    while True:
        sleep(1)


def refresh_meta():
    names = get_all_names()
    meta = get_meta_file()
    for name in names:
        if name not in meta.keys() and is_dkg_passed(name):
            endpoint = get_schain_endpoint(name)
            meta[name] = {
                'endpoint': endpoint
            }
    update_meta_file(meta)


def main():
    assert os.path.isfile(ABI_FILEPATH), "ABI not found"
    if not os.path.isfile(META_DATA_PATH):
        create_meta_file()
    create_tables()
    refresh_meta()
    run_collectors()


if __name__ == '__main__':
    init_logger()
    main()
