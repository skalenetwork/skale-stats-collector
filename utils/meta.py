from collector import META_DATA_PATH
from helper import write_json, read_json


def create_meta_file():
    empty_data = {
        'schains': {}
    }
    write_json(META_DATA_PATH, empty_data)


def get_schain_meta(schain_name):
    meta = read_json(META_DATA_PATH)
    return meta.get(schain_name)


def get_schain_endpoint(schain_name):
    meta = get_schain_meta(schain_name)
    if meta:
        return meta.get(schain_name)
    else:
        return None
