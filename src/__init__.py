import os

ENDPOINT = os.environ.get('ETH_ENDPOINT')
ETH_API_KEY = os.environ.get('ETH_API_KEY')
PROXY_DOMAIN_NAME = os.environ.get('PROXY_DOMAIN')
SCHAIN_NAMES = os.environ.get('SCHAIN_NAMES')


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.join(DIR_PATH, os.pardir)
DATA_DIR = os.path.join(PROJECT_PATH, 'data')
META_DATA_PATH = os.path.join(DATA_DIR, 'meta.json')
META_DUMP_PATH = os.path.join(DATA_DIR, 'meta-dump.json')
ABI_FILEPATH = os.path.join(DATA_DIR, 'abi.json')


DB_NAME = 'stats.db'
DB_DUMP_NAME = 'stats-dump.db'
DB_FILE_PATH = os.path.join(DATA_DIR, DB_NAME)
DB_DUMP_PATH = os.path.join(DATA_DIR, DB_DUMP_NAME)
NETWORK_STATS_FILE_PATH = os.path.join(DATA_DIR, 'network-stats.json')

# Stats API
FLASK_APP_PORT = os.environ.get('FLASK_APP_PORT')
FLASK_APP_HOST = os.environ.get('FLASK_APP_HOST')
FLASK_HOST_PORT = os.environ.get('FLASK_HOST_PORT')
