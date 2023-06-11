from web3 import Web3, HTTPProvider

class Collector:
    def __init__(self, schain_name, endpoint):
        self.schain_name = schain_name
        self.endpoint = endpoint
        self.web3 = Web3(self.endpoint)
        self.last_block = self.get_last_block()
        self.stats = {}

    def catchup_blocks(self):
        try:
            latest_block = self.web3.eth.get_block_number()
            for i in range(self.last_block, latest_block):
                block = self.web3.eth.get_block(i, True)
                self.update_daily_stats(block)
        except:
            pass

    def update_daily_stats(self, block):
        print(block)

    def get_last_block(self):
        return 0
