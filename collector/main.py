import os

from collector import META_DATA_PATH
from utils.logger import init_logger
from utils.meta import create_meta_file


def main():
    if not os.path.isfile(META_DATA_PATH):
        create_meta_file()


if __name__ == '__main__':
    init_logger()
    main()
