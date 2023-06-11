import logging

from web3 import Web3, HTTPProvider

from core.collector.database import get_data, insert_new_block

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, schain_name, endpoint):
        self.schain_name = schain_name
        self.endpoint = endpoint
        self.web3 = Web3(HTTPProvider(self.endpoint))
        self.last_block = self.get_last_block()
        self.stats = {}

    def catchup_blocks(self):
        try:
            latest_block = self.web3.eth.get_block_number()
            for i in range(self.last_block, latest_block):
                block = self.web3.eth.get_block(i, True)
                self.update_daily_stats(block)
        except Exception as error:
            logger.info(error)
            pass

    def update_daily_stats(self, block):
        users = [tx['from'] for tx in block['transactions']]
        # TODO: convert ts
        insert_new_block(self.schain_name, block['timestamp'], len(users), users)

    def get_last_block(self):
        return 0

    def get_stats(self):
        pass
