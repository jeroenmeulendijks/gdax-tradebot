import json, requests, datetime

from candles import *
from operator import itemgetter

class DemoOrderBook(object):
    # Demo class which connects to gdax but never actually creates an order

    def __init__(self, productIds):
        self.priceCount = 0
        self.productIdLen = len(productIds)
        self.productIds = productIds

        # Sort list of lists with in each item: [ time, low, high, open, close, volume ]
        self.candles = {}
        print("Available demo candles:")
        for key, val in CANDLES.items():
            print (key, "=>", len(val))
            self.candles[key] = sorted(val, key=itemgetter(0))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    async def handle_message(self):
        message = {}

        productId = self.productIds[self.priceCount % self.productIdLen]

        candle = self.candles[productId][self.priceCount]
        # candle is stored as [ time, low, high, open, close, volume ]
        message['type'] = 'match'
        message['product_id'] = productId
        message['time'] = "{}.000Z".format(datetime.datetime.utcfromtimestamp(candle[0]).isoformat())
        message['low'] = candle[1]
        message['high'] = candle[2]
        message['open'] = candle[3]
        message['close'] = candle[4]
        message['size'] = candle[5]

        self.priceCount += 1
        if (self.priceCount > len(self.candles[productId])):
            self.priceCount = 0
        return message

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
