from collector import META_DATA_PATH
from helper import write_json, read_json


def create_meta_file():
    empty_data = {
    }
    write_json(META_DATA_PATH, empty_data)


def get_meta_file():
    return read_json(META_DATA_PATH)


def get_schain_meta(schain_name):
    meta = get_meta_file()
    return meta.get(schain_name)


def get_schain_endpoint(schain_name):
    meta = get_schain_meta(schain_name)
    if meta:
        return meta.get(schain_name)
    else:
        return None


def update_meta_file(meta_data):
    write_json(META_DATA_PATH, meta_data)