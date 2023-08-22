import concurrent
import json
import logging
from datetime import datetime

import requests as requests
from web3 import Web3, HTTPProvider

from core import ETH_API_KEY
from core.collector.database import (get_daily_data, update_daily_prices,
                                     insert_new_block_data, insert_new_daily_users, get_montly_data, get_total_data)
from core.utils.meta import get_schain_endpoint, get_meta_file, update_meta_file

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.ERROR)


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
            logger.info(f'Catching up blocks from {first_batch_block} to {latest_block}')
            while first_batch_block < latest_block:
                self.catchup_batch_blocks(first_batch_block, last_batch_block)
                first_batch_block = last_batch_block
                last_batch_block = min(first_batch_block + 1000, latest_block)
        except Exception as error:
            logger.info(error)
            pass

    def catchup_batch_blocks(self, first_batch_block, last_batch_block):
        logger.info(f'Collecting blocks from {first_batch_block} to {last_batch_block}')
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as e:
            results = []
            futures = [e.submit(self.download, block_num) for block_num in
                   range(first_batch_block, last_batch_block)]
            for thread in concurrent.futures.as_completed(futures):
                results.append(thread.result())
        logger.info(f'Writing {len(results)} blocks to DB')
        self.insert_block_batch(results)
        self.update_last_block(last_batch_block)

    def download(self, block_number):
        return self.web3.eth.get_block(block_number, True)

    def insert_block_batch(self, batch):
        users_daily = {}
        for block in batch:
            date = str(datetime.fromtimestamp(block['timestamp']).date())
            users_daily[date] = users_daily.get(date, []) + [tx['from'] for tx in block['transactions']]
            gas = block['gasUsed']
            insert_new_block_data(self.schain_name, block['number'], date, len(block['transactions']), gas)
        for date in users_daily:
            if len(users_daily[date]) > 0:
                insert_new_daily_users(self.schain_name, date, users_daily[date])

    def update_last_block(self, last_block):
        meta = get_meta_file()
        meta[self.schain_name]['last_updated_block'] = last_block
        update_meta_file(meta)

    def get_last_block(self):
        return get_meta_file()[self.schain_name].get('last_updated_block', 0)

    def get_daily_stats(self):
        return {
            'group_by_month': get_montly_data(self.schain_name),
            'total': get_total_data(self.schain_name)
        }


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
