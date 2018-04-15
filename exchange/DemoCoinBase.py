import json, requests, datetime

from candles import *
from operator import itemgetter

class DemoCoinBase(object):
    # Demo class which connects to gdax but never actually creates an order

    def __init__(self, productId):
        self.priceCount = 0
        self.productId = productId

        # Sort list of lists with in each item: [ time, low, high, open, close, volume ]
        self.candles = {}
        print("Available demo candles:")
        for key, val in CANDLES.items():
            print (key, "=>", len(val))
            self.candles[key] = sorted(val, key=itemgetter(0))

    async def get_time(self):
        time = {}
        time['epoch'] = self.candles[self.productId][self.priceCount][0]
        time['iso'] = datetime.datetime.utcfromtimestamp(time['epoch']).isoformat()
        return time

    def getBalance(self, currency):
        return float(100.0)

    async def get_product_ticker(self):
        # Just use the high price
        ticker = {}
        ticker['price'] = self.candles[self.productId][self.priceCount][2]
        self.priceCount += 1
        return ticker

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
