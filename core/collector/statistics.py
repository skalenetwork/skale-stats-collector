import concurrent
import json
import logging
from datetime import datetime

import requests as requests
from web3 import Web3, HTTPProvider

from core import ETH_API_KEY
from core.collector.database import get_data, insert_new_block, update_daily_prices
from core.utils.meta import get_schain_endpoint

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, schain_name, from_block=None, to_block=None):
        self.schain_name = schain_name
        self.endpoint = get_schain_endpoint(schain_name)
        self.web3 = Web3(HTTPProvider(self.endpoint))
        self.last_block = from_block if from_block else self.get_last_block()
        self.to_block = to_block
        self.stats = {}

    def catchup_blocks(self):
        try:
            latest_block = self.to_block if self.to_block else self.web3.eth.get_block_number()
            first_batch_block = self.last_block
            last_batch_block = min(first_batch_block + 1000, latest_block)
            while first_batch_block < latest_block:
                self.catchup_batch_blocks(first_batch_block, last_batch_block)
                first_batch_block = last_batch_block
                last_batch_block = min(first_batch_block + 1000, latest_block)
        except Exception as error:
            logger.info(error)
            pass

    def catchup_batch_blocks(self, first_batch_block, last_batch_block):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as e:
            res = []
            fut = [e.submit(self.download, j) for j in range(first_batch_block, last_batch_block)]
            for r in concurrent.futures.as_completed(fut):
                res.append(r.result())
        logger.info(f'Writing {len(res)} blocks to DB')
        for block in res:
            self.update_daily_stats(block)

    def download(self, j):
        return self.web3.eth.get_block(j, True)

    def update_daily_stats(self, block):
        users = [tx['from'] for tx in block['transactions']]
        date = datetime.fromtimestamp(block['timestamp'])
        gas = block['gasUsed']
        insert_new_block(self.schain_name, block['number'], str(date.date()), len(users), users, gas)

    def get_last_block(self):
        return 0

    def get_daily_stats(self, date):
        return get_data(self.schain_name)


class PricesCollector:
    ETH_API_URL='https://api.etherscan.io/api'

    def fetch_daily_prices(self, start_date, end_date):
        _gas_prices = self.get_gas_prices(start_date, end_date)
        _gas_prices = {i['UTCDate']: i['avgGasPrice_Wei'] for i in _gas_prices}

        _eth_prices = self.get_eth_prices(start_date, end_date)
        _eth_prices = {i['UTCDate']: i['value'] for i in _eth_prices}

        keys = _eth_prices.keys()
        values = zip(_eth_prices.values(), _gas_prices.values())
        data = dict(zip(keys, values))
        update_daily_prices(data)

    @staticmethod
    def get_gas_prices(start_date, end_date):
        url = f'{PricesCollector.ETH_API_URL}?module=stats&action=dailyavggasprice&' \
              f'startdate={start_date}&' \
              f'enddate={end_date}&' \
              f'sort=asc&' \
              f'apikey={ETH_API_KEY}'
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(response.text)['result']
            return data
        except requests.RequestException as e:
            logger.warning(f'Could not download gas_prices: {e}')

    @staticmethod
    def get_eth_prices(start_date, end_date):
        url = f'{PricesCollector.ETH_API_URL}?module=stats&action=ethdailyprice&' \
              f'startdate={start_date}&' \
              f'enddate={end_date}&' \
              f'sort=asc&' \
              f'apikey={ETH_API_KEY}'
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(response.text)['result']
            return data
        except requests.RequestException as e:
            logger.warning(f'Could not download gas_prices: {e}')
