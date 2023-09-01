import logging
import os

from src import META_DATA_PATH, ABI_FILEPATH, SNAPSHOT_FILE_PATH
from src.collector.core.statistics import aggregate_network_stats, verify_network_stats_data
from src.collector.database.ops import create_tables, update_daily_price_stats
from src.collector.core.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from src.collector.core.fetchers import Collector, PricesCollector
from src.utils.helper import daemon, write_json
from src.utils.logger import init_logger
from src.utils.meta import create_meta_file, get_meta_file, update_meta_file

logger = logging.getLogger(__name__)


@daemon(delay=600)
def update_statistics():
    refresh_meta()
    names = get_all_names()
    for name in names:
        update_daily_price_stats(name)
        logger.info(f'Start catchup for {name}')
        collector = Collector(name)
        collector.catchup_blocks()
    PricesCollector().update_gas_saved_stats(names)
    logger.info('Aggregating network stats...')
    network_stats = aggregate_network_stats(names)
    logger.info('Verifying network stats...')
    write_json(SNAPSHOT_FILE_PATH, network_stats)
    verify_network_stats_data(network_stats)
    logger.info('Stats updated')


def refresh_meta():
    names = get_all_names()
    meta = get_meta_file()
    for name in names:
        if name not in meta['schains'].keys() and is_dkg_passed(name):
            endpoint = get_schain_endpoint(name)
            meta['schains'][name] = {
                'endpoint': endpoint
            }
    update_meta_file(meta)


def main():
    assert os.path.isfile(ABI_FILEPATH), "ABI not found"
    if not os.path.isfile(META_DATA_PATH):
        create_meta_file()
    create_tables()
    update_statistics()


if __name__ == '__main__':
    init_logger()
    main()
