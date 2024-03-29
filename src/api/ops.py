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

from src import NETWORK_STATS_FILE_PATH
from src.utils.helper import read_json


def get_legacy_stats(schain_name=None):
    raw_data = read_json(NETWORK_STATS_FILE_PATH)
    if schain_name:
        data_to_convert = raw_data['schains'].get(schain_name)
    else:
        data_to_convert = raw_data['summary']
    if not data_to_convert:
        return {}
    if not schain_name:
        return {
            'schains_number': raw_data['schains_number'],
            'inserted_at': raw_data['inserted_at'],
            **convert_to_legacy(data_to_convert)
        }
    return {
        'schain_name': schain_name,
        'inserted_at': raw_data['inserted_at'],
        **convert_to_legacy(data_to_convert)
    }


def get_latest_stats(schain_name=None):
    data = read_json(NETWORK_STATS_FILE_PATH)
    if schain_name:
        data_to_return = data['schains'].get(schain_name)
        data_to_return.update({
            'schain_name': schain_name,
            'inserted_at': data['inserted_at']
        })
        return data_to_return
    return data


def convert_to_legacy(data):
    converted_data = {
        'block_count_total': data['total']['block_count_total'],
        "block_count_30_days": data['total_30d']['block_count_total'],
        "block_count_7_days": data['total_7d']['block_count_total'],
        "gas_fees_total_30_days_eth": data['total_30d']['gas_fees_total_eth'],
        "gas_fees_total_30_days_gwei": data['total_30d']['gas_fees_total_gwei'],
        "gas_fees_total_30_days_usd": data['total_30d']['gas_fees_total_usd'],
        "gas_fees_total_7_days_eth": data['total_7d']['gas_fees_total_eth'],
        "gas_fees_total_7_days_gwei": data['total_7d']['gas_fees_total_gwei'],
        "gas_fees_total_7_days_usd": data['total_7d']['gas_fees_total_usd'],
        "gas_fees_total_eth": data['total']['gas_fees_total_eth'],
        "gas_fees_total_gwei": data['total']['gas_fees_total_gwei'],
        "gas_fees_total_usd": data['total']['gas_fees_total_usd'],
        "gas_total_used": data['total']['gas_total_used'],
        "gas_total_used_30_days": data['total_30d']['gas_total_used'],
        "gas_total_used_7_days": data['total_7d']['gas_total_used'],
        'max_tps_last_7_days': 0,
        'max_tps_last_30_days': 0,
        "tx_count_30_days": data['total_30d']['tx_count_total'],
        "tx_count_7_days": data['total_7d']['tx_count_total'],
        "tx_count_total": data['total']['tx_count_total'],
        "unique_tx_count_30_days": data['total_30d']['tx_count_total'],
        "unique_tx_count_7_days": data['total_7d']['tx_count_total'],
        "unique_tx_count_total": data['total']['tx_count_total'],
        "user_count_30_days": data['total_30d']['users_count_total'],
        "user_count_7_days": data['total_7d']['users_count_total'],
        "user_count_total": data['total']['users_count_total']
    }
    group_by_month = []
    for month in data['group_by_month']:
        month_data = data['group_by_month'][month]
        group_by_month.append({
            "data_by_days": False,
            "gas_fees_total_eth": month_data['gas_fees_total_eth'],
            "gas_fees_total_gwei": month_data['gas_fees_total_gwei'],
            "gas_fees_total_usd": month_data['gas_fees_total_usd'],
            "gas_total_used": month_data['gas_total_used'],
            "tx_count": month_data['tx_count_total'],
            "tx_date": month,
            "unique_tx": month_data['tx_count_total'],
            "user_count": month_data.get('users_count_total', 0)
        })
    converted_data['group_by_days'] = []
    converted_data['group_by_months'] = group_by_month
    return converted_data
