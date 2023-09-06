#   -*- coding: utf-8 -*-
#
#   This file is part of skale-stats-collector
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os

from src import META_DATA_PATH, ABI_FILEPATH, SNAPSHOT_FILE_PATH
from src.collector.core.statistics import aggregate_network_stats, verify_network_stats_data
from src.collector.database.ops import create_tables, update_daily_price_stats, last_pulled_block
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
            last_updated_block = last_pulled_block(name)
            meta['schains'][name] = {
                'endpoint': endpoint,
                'last_updated_block': last_updated_block
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
