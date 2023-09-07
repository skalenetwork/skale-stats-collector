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
from datetime import datetime
from src.collector.database.ops import get_total_data, count_pulled_blocks
from src.utils.helper import update_dict
from src.utils.meta import get_last_block

logger = logging.getLogger(__name__)


def get_schain_stats(schain_name):
    return {
        'total': get_total_data(schain_name),
        'total_7d': get_total_data(schain_name, days_before=7),
        'total_30d': get_total_data(schain_name, days_before=30),
        'group_by_month': get_total_data(schain_name, group_by_month=True)
    }


def verify_schain_stats_data(schain_name, stats_data):
    total_blocks_meta = get_last_block(schain_name)
    total_blocks_db = count_pulled_blocks(schain_name)
    stats_blocks_sum = stats_data['total']['block_count_total']
    if total_blocks_meta == total_blocks_db and stats_blocks_sum == total_blocks_db:
        return True
    return False


def verify_network_stats_data(stats):
    all_data_valid = True
    schains = stats['schains']
    for schain_name in schains:
        is_stats_valid = verify_schain_stats_data(schain_name, schains[schain_name])
        if not is_stats_valid:
            all_data_valid = False
            logger.error(f'Stats data for {schain_name} is not valid')
    if all_data_valid:
        logger.info('Network stats is valid')
    return all_data_valid


def aggregate_network_stats(names):
    stats = {
        'schains_number': len(names),
        'summary': {
            'total': {},
            'total_7d': {},
            'total_30d': {},
            'group_by_month': {}
        },
        'schains': {}
    }
    for name in names:
        logger.info(f'Aggregating stats for {name}')
        schain_data = get_schain_stats(name)
        stats['schains'].update({
            name: schain_data
        })
        update_dict(stats['summary']['total'], schain_data['total'])
        update_dict(stats['summary']['total_7d'], schain_data['total_7d'])
        update_dict(stats['summary']['total_30d'], schain_data['total_30d'])
        update_dict(stats['summary']['group_by_month'], schain_data['group_by_month'])
    stats['inserted_at'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    return stats
