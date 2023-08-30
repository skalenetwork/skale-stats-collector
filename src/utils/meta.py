from src import META_DATA_PATH
from src.utils.helper import write_json, read_json


def create_meta_file():
    empty_data = {
        'schains': {}
    }
    write_json(META_DATA_PATH, empty_data)


def get_meta_file():
    return read_json(META_DATA_PATH)


def get_schain_meta(schain_name):
    meta = get_meta_file()['schains']
    return meta.get(schain_name)


def get_schain_endpoint(schain_name):
    meta = get_schain_meta(schain_name)
    if meta:
        return meta.get('endpoint')
    else:
        return None


def update_last_price_date(last_update_date):
    meta = get_meta_file()
    meta['last_price_update'] = last_update_date
    update_meta_file(meta)


def update_last_block(schain_name, last_block):
    meta = get_meta_file()
    meta['schains'][schain_name]['last_updated_block'] = last_block
    update_meta_file(meta)


def get_last_block(schain_name):
    return get_schain_meta(schain_name).get('last_updated_block', 0)


def get_last_price_date():
    meta = get_meta_file()
    return meta.get('last_price_update', '2021-01-01')


def update_meta_file(meta_data):
    write_json(META_DATA_PATH, meta_data)
