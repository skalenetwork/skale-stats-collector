import os

from core import META_DATA_PATH, ABI_FILEPATH
from core.collector.database import create_tables
from core.collector.endpoints import get_all_names, is_dkg_passed, get_schain_endpoint
from core.collector.statistics import Collector
from core.utils.logger import init_logger
from core.utils.meta import create_meta_file, get_meta_file, update_meta_file


def run_collectors():
    pass


def refresh_meta():
    names = get_all_names()
    meta = get_meta_file()
    for name in names:
        if name not in meta.keys() and is_dkg_passed(name):
            endpoint = get_schain_endpoint(name)
            meta[name] = endpoint
    update_meta_file(meta)


def main():
    assert os.path.isfile(ABI_FILEPATH), "ABI not found"
    if not os.path.isfile(META_DATA_PATH):
        create_meta_file()
    create_tables()
    run_collectors()


if __name__ == '__main__':
    init_logger()
    main()
