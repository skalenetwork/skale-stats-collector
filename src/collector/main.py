import logging
import os
from datetime import datetime

from src import META_DATA_PATH, ABI_FILEPATH, SNAPSHOT_FILE_PATH
from src.collector.database.ops import create_tables, get_schain_stats
from src.collector.core.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from src.collector.core.fetchers import Collector, PricesCollector
from src.utils.helper import daemon, write_json
from src.utils.logger import init_logger
from src.utils.meta import create_meta_file, get_meta_file, update_meta_file

logger = logging.getLogger(__name__)


def update_dict(target_dict, chain_dict):
    for key in chain_dict:
        if type(chain_dict[key]) is dict:
            if target_dict.get(key) is None:
                target_dict[key] = {}
            update_dict(target_dict[key], chain_dict[key])
        else:
            target_dict[key] = target_dict.get(key, 0) + chain_dict[key]


def aggregate_schain_stats(names):
    stats = {
        'schains_number': len(names),
        'summary': {
            'total': {},
            'total_7d': {},
            'total_30d': {},
            'group_by_month': {}
        }
    }
    for name in names:
        logger.info(f'Aggregating stats for {name}')
        schain_data = get_schain_stats(name)
        stats.update({
            name: schain_data
        })
        update_dict(stats['summary']['total'], schain_data['total'])
        update_dict(stats['summary']['total_7d'], schain_data['total_7d'])
        update_dict(stats['summary']['total_30d'], schain_data['total_30d'])
        update_dict(stats['summary']['group_by_month'], schain_data['group_by_month'])
    stats['inserted_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    return stats


@daemon(delay=600)
def update_statistics():
    refresh_meta()
    names = get_all_names()
    PricesCollector().update_gas_saved_stats(names)
    for name in names:
        logger.info(f'Start catchup for {name}')
        collector = Collector(name)
        collector.catchup_blocks()
    logger.info('Aggregating schain stats...')
    snapshot_data = aggregate_schain_stats(names)
    write_json(SNAPSHOT_FILE_PATH, snapshot_data)
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
