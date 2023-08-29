import logging
from datetime import datetime
from src.collector.database.ops import get_total_data

logger = logging.getLogger(__name__)


def get_schain_stats(schain_name):
    return {
        'total': get_total_data(schain_name),
        'total_7d': get_total_data(schain_name, days_before=7),
        'total_30d': get_total_data(schain_name, days_before=30),
        'group_by_month': get_total_data(schain_name, group_by_month=True)
    }


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
