import os

ENDPOINT = os.environ.get('ETH_ENDPOINT')
ETH_API_KEY = os.environ.get('ETH_API_KEY')
PROXY_DOMAIN_NAME = os.environ.get('PROXY_DOMAIN')


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.join(DIR_PATH, os.pardir)
DATA_DIR = os.path.join(PROJECT_PATH, 'data')
META_DATA_PATH = os.path.join(DATA_DIR, 'meta.json')
ABI_FILEPATH = os.path.join(DATA_DIR, 'abi.json')


DB_NAME = 'stats.db'
DB_FILE_PATH = os.path.join(DATA_DIR, DB_NAME)