import json
import logging
import os
from datetime import datetime
from threading import Thread
from time import sleep

from core import META_DATA_PATH, ABI_FILEPATH
from core.collector.database import create_tables, refetch_daily_price_stats, get_daily_data, merge_bases, \
    get_total_data, get_schain_stats
from core.collector.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from core.collector.statistics import Collector, PricesCollector
from core.utils.helper import daemon
from core.utils.logger import init_logger
from core.utils.meta import create_meta_file, get_meta_file, update_meta_file

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
            'group_by_month': {}
        }
    }
    for name in names:
        print(name)
        schain_data = get_schain_stats(name)
        stats.update({
            name: schain_data
        })
        update_dict(stats['summary']['total'], schain_data['total'])
        update_dict(stats['summary']['group_by_month'], schain_data['group_by_month'])
    stats['inserted_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    return stats


@daemon(delay=600)
def update_statistics():
    refresh_meta()
    names = get_all_names()
    for name in names:
        logger.info(f'Start catchup for {name}')
        collector = Collector(name)
        collector.catchup_blocks()
    aggregate_schain_stats(names)


def run_collectors():
    # names = get_all_names()
    # st = aggregate_schain_stats(names)
    # print(json.dumps(st, indent=4))
    names = get_meta_file()
    for name in names:
        logger.info(f'Start catchup for {name}')
        collector = Collector(name)
        collector.catchup_blocks()
        # print(json.dumps(collector.get_daily_stats(), indent=4))
        # Thread(target=collector.catchup_blocks, daemon=True, name=name).start()
    # while True:
    #     sleep(1)


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
    update_statistics()


if __name__ == '__main__':
    init_logger()
    main()
