import os

from collector import META_DATA_PATH
from collector.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from utils.logger import init_logger
from utils.meta import create_meta_file, get_meta_file, update_meta_file


def refresh_meta():
    names = get_all_names()
    meta = get_meta_file()
    for name in names:
        if name not in meta.keys() and is_dkg_passed(name):
            endpoint = get_schain_endpoint(name)
            meta[name] = endpoint
    update_meta_file(meta)


def main():
    if not os.path.isfile(META_DATA_PATH):
        create_meta_file()


if __name__ == '__main__':
    init_logger()
    main()
