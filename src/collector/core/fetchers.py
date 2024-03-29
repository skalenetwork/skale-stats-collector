#   -*- coding: utf-8 -*-
#
#   This file is part of skale-stats-collector
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import concurrent
import logging
from datetime import datetime
from web3 import Web3, HTTPProvider

from src import ETH_API_KEY
from src.collector.database.ops import (insert_new_daily_prices, insert_new_block_data,
                                        insert_new_daily_users, update_daily_price_stats)
from src.utils.helper import download_via_url
from src.utils.meta import (get_schain_endpoint, update_last_block, get_last_block,
                            get_last_price_date, update_last_price_date)

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.ERROR)


class Collector:
    BLOCKS_BATCH_SIZE = 1000

    def __init__(self, schain_name, from_block=None, to_block=None):
        self.schain_name = schain_name
        self.endpoint = get_schain_endpoint(schain_name)
        self.web3 = Web3(HTTPProvider(self.endpoint))
        self.last_block = from_block if from_block else get_last_block(self.schain_name)
        self.to_block = to_block
        self.stats = {}

    def catchup_blocks(self):
        try:
            latest_block = self.to_block if self.to_block else self.web3.eth.get_block_number()
            first_batch_block = self.last_block
            last_batch_block = min(first_batch_block + self.BLOCKS_BATCH_SIZE, latest_block)
            logger.info(f'Catching up blocks from {first_batch_block} to {latest_block}')
            while first_batch_block < latest_block:
                self.catchup_batch_blocks(first_batch_block, last_batch_block)
                first_batch_block = last_batch_block
                last_batch_block = min(first_batch_block + self.BLOCKS_BATCH_SIZE, latest_block)
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
        update_last_block(self.schain_name, last_batch_block)

    def download(self, block_number):
        return self.web3.eth.get_block(block_number, True)

    def insert_block_batch(self, batch):
        users_daily = {}
        for block in batch:
            date = str(datetime.fromtimestamp(block['timestamp']).date())
            users_daily[date] = (users_daily.get(date, []) +
                                 [tx['from'] for tx in block['transactions']])
            gas = block['gasUsed']
            insert_new_block_data(self.schain_name, block['number'], date,
                                  len(block['transactions']), gas)
        for date in users_daily:
            if len(users_daily[date]) > 0:
                insert_new_daily_users(self.schain_name, date, users_daily[date])


class PricesCollector:
    ETH_API_URL = 'https://api.etherscan.io/api'

    def __init__(self):
        self.last_updated = get_last_price_date()

    def update_gas_saved_stats(self, schain_names):
        current_date = datetime.utcnow().date()
        if str(current_date) == self.last_updated:
            return
        logger.info(f'Fetching gas prices from {self.last_updated} to {current_date}')
        new_prices_fetched = self.fetch_daily_prices(self.last_updated, current_date)
        if new_prices_fetched:
            for name in schain_names:
                update_daily_price_stats(name)
                logger.info(f'Gas saved stats updated for {name}')
            update_last_price_date(str(current_date))
        else:
            logger.warning('Gas saved stats not updated')

    def fetch_daily_prices(self, start_date, end_date):
        _gas_prices = self.get_gas_prices(start_date, end_date)
        _gas_prices = {i['UTCDate']: i['avgGasPrice_Wei'] for i in _gas_prices}

        _eth_prices = self.get_eth_prices(start_date, end_date)
        _eth_prices = {i['UTCDate']: i['value'] for i in _eth_prices}

        keys = _eth_prices.keys()
        values = zip(_eth_prices.values(), _gas_prices.values())
        data = dict(zip(keys, values))
        if data:
            insert_new_daily_prices(data)
            logger.info('New prices were added to db')
            return True
        return False

    @staticmethod
    def get_gas_prices(start_date, end_date):
        url = f'{PricesCollector.ETH_API_URL}?module=stats&action=dailyavggasprice&' \
              f'startdate={start_date}&' \
              f'enddate={end_date}&' \
              f'sort=asc&' \
              f'apikey={ETH_API_KEY}'
        return download_via_url(url)

    @staticmethod
    def get_eth_prices(start_date, end_date):
        url = f'{PricesCollector.ETH_API_URL}?module=stats&action=ethdailyprice&' \
              f'startdate={start_date}&' \
              f'enddate={end_date}&' \
              f'sort=asc&' \
              f'apikey={ETH_API_KEY}'
        return download_via_url(url)
