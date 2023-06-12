import concurrent
import logging
from datetime import datetime
from web3 import Web3, HTTPProvider

from core.collector.database import get_data, insert_new_block
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
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as e:
                res = []
                fut = [e.submit(self.download, j) for j in range(self.last_block, latest_block)]
                for r in concurrent.futures.as_completed(fut):
                    res.append(r.result())
            for block in res:
                self.update_daily_stats(block)
        except Exception as error:
            logger.info(error)
            pass

    def download(self, j):
        return self.web3.eth.get_block(j, True)

    def update_daily_stats(self, block):
        users = [tx['from'] for tx in block['transactions']]
        date = datetime.fromtimestamp(block['timestamp'])
        gas = block['gasUsed']
        insert_new_block(self.schain_name, str(date.date()), len(users), users, gas)

    def get_last_block(self):
        return 0

    def get_daily_stats(self, date):
        return get_data(self.schain_name, date)
