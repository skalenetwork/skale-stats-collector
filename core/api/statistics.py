from core import SNAPSHOT_FILE_PATH
from core.utils.helper import read_json


def get_latest_stats():
    raw_data = read_json(SNAPSHOT_FILE_PATH)
    result = {
        'schains_number': raw_data['schains_number'],
        'inserted_at': raw_data['inserted_at']
    }
    raw_data = raw_data.get('summary')
    result.update(convert_to_legacy(raw_data))
    return result


def get_latest_schain_stats(schain_name):
    raw_data = read_json(SNAPSHOT_FILE_PATH)
    if not raw_data.get(schain_name):
        return {}
    result = {
        'schain_name': raw_data['schains_number'],
        'inserted_at': raw_data['inserted_at']
    }
    raw_data = raw_data.get(schain_name)
    result.update(convert_to_legacy(raw_data))
    return result


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
    converted_data['group_by_month'] = group_by_month
    return converted_data