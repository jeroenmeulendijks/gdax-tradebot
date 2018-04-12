import json, requests
from exchange.CoinBaseAuthenticate import CoinbaseExchangeAuth
from exchange.CoinBase import Coinbase

from candles import *
from operator import itemgetter

class DemoCoinBase(Coinbase):
    # Demo class which connects to gdax but never actually creates an order

    def __init__(self, api_key, secret_key, passphrase, api_url):
        super(DemoCoinBase, self).__init__(api_key, secret_key, passphrase, api_url)
        self.priceCount = 0

        # Sort list of lists with in each item: [ time, low, high, open, close, volume ]
        self.candles = {}
        print("Available demo candles:")
        for key, val in CANDLES.items():
            print (key, "=>", len(val))
            self.candles[key] = sorted(val, key=itemgetter(0))

    def getTime(self):
        return self.priceCount #self.candles[self.requestedProductId][self.priceCount][0]

    def getBalance(self, currency):
        return float(100.0)

    def getProductId(self, base_currency, quote_currency):
        self.requestedProductId = "{}-{}".format(base_currency, quote_currency)
        return self.requestedProductId

    def getPrice(self, product_id):
        # Just use the high price
        price = self.candles[product_id][self.priceCount][2]
        self.priceCount += 1
        return price

    def determinePrice(self, product_id, option):
        return self.candles[product_id][self.priceCount][2]

    def buy(self, product_id, quantity, price):
        return self._createDemoOrderResult("buy", product_id, quantity, price)

    def sell(self, product_id, quantity, price, upper):
        return self._createDemoOrderResult("sell", product_id, quantity, price)

    def getOrderStatus(self, order_id):
        return "done"

    def cancelOrder(self, order_id):
        return [order_id]

    def _createDemoOrderResult(self, side, product_id, quantity, price):
        order = {}
        order['id'] = 'DUMMY_TRANSACTION'
        order['price'] = price
        order['size'] = quantity
        order['product_id'] = product_id
        order['side'] = side
        order['stp'] = 'dc'
        order['type'] = 'limit'
        order['time_in_force'] = 'GTC'
        order['post_only'] = 'false'
        order['created_at'] = ''
        order['fill_fees'] = '0.0000000000000000'
        order['filled_size'] = '0.00000000'
        order['executed_value'] = '0.0000000000000000'
        order['status'] = 'done'
        order['settled'] = False
        return order
