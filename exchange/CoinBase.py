import json, requests
from exchange.CoinBaseAuthenticate import CoinbaseExchangeAuth

import datetime

class Coinbase(object):
    # Class used to perform different actions on the GDAX API

    def __init__(self, api_key, secret_key, passphrase, api_url):
        self.api_url = api_url
        self.auth = CoinbaseExchangeAuth(api_key, secret_key, passphrase, api_url)

    def _getJson(self, endPoint, data = "", timeout = 30):
        req = requests.get(self.api_url + endPoint, data = data, auth = self.auth, timeout = timeout)
        # TODO: check if return value is valid json?!
        return req.json()

    def _postJson(self, endPoint, data = "", timeout = 30):
        req = requests.post(self.api_url + endPoint, data = data, auth = self.auth, timeout = timeout)
        # TODO: check if return value is valid json?!
        return req.json()

    def getTime(self):
        return self._getJson('time')['epoch']

    def getBalance(self, currency):
        accounts = self._getJson('accounts')

        # Find index corresponding to currency
        index = next(index for (index, d) in enumerate(accounts) if d['currency'] == currency)
        return float(accounts[index]['balance'])

    def getProductId(self, base_currency, quote_currency):
        products = self._getJson('products')

        # Find index corresponding to pair
        index = next(index for (index, d) in enumerate(products) if ((d['base_currency'] == base_currency) and (d['quote_currency'] == quote_currency)))
        return products[index]['id']

    def getPrice(self, product_id):
        product = self._getJson('products/' + product_id + '/ticker')
        return product['price']

    def determinePrice(self, product_id, option):
        parameters = {'level': '1'}
        book = self._getJson('products/' + product_id + '/book', json.dumps(parameters))

        if option == 'buy':
            buy_price = float(book['bids'][0][0]) - 0.01
            return float(buy_price)
        if option == 'sell':
            sell_price = float(book['asks'][0][0]) + 0.01
            return float(sell_price)

    def buy(self, product_id, quantity, price):
        # Rounded down to 7dp
        quantity = (quantity // 0.0000001) / 10000000
        parameters = {
            'type': 'limit',
            'size': quantity,
            'price': price,
            'side': 'buy',
            'product_id': product_id,
            'time_in_force': 'GTC',
            'post_only': True
        }
        return self._postJson('orders', json.dumps(parameters))

    def sell(self, product_id, quantity, price, upper):
        # Round price to 2DP
        price = round(float(price), 2)
        if upper is True:
            parameters = {
                'type': 'limit',
                'size': quantity,
                'price': price,
                'side': 'sell',
                'product_id': product_id,
                'time_in_force': 'GTC',
                'post_only': True
            }
        else:
            time_to_cancel = 'hour'
            parameters = {
                'type': 'limit',
                'size': quantity,
                'price': price,
                'side': 'sell',
                'product_id': product_id,
                'time_in_force': 'GTT',
                'cancel_after': time_to_cancel,
                'post_only': True
            }
        return self._postJson('orders', json.dumps(parameters))

    def cancelOrder(self, order_id):
        request = requests.delete(self.api_url + 'orders/' + order_id , auth=self.auth)
        return request.json()

    def getOrders(self):
        return self._getJson('orders')

    def cancelOpenOrders(self):
        open_orders = self.getOrders()
        if(len(open_orders) > 0):
            for order in open_orders:
                self.cancelOrder(order['id'])

    def getHistoricRates(self, product_id, startDate, endDate):
        # Returns a list with: [ time, low, high, open, close, volume ]
        # GDAX API will return at most 300 datapoints so the granularity should limit the datapoints to max 300 points
        # Available granularity values are {60, 300, 900, 3600, 21600, 86400}
        granularities = [60, 300, 900, 3600, 21600, 86400]
        maxCandles = 300
        timeDiv = endDate - startDate
        timeDiffInSeconds = divmod(timeDiv.days * 86400 + timeDiv.seconds, 1)[0]
        g = timeDiffInSeconds / maxCandles

        #print("Start: {} End: {} Granularity: {}".format(startDate, endDate, g))

        if (g < granularities[-1]):
            granularity = min([i for i in granularities if i >= g])
            #return [[1515538800, 1065, 1098.5, 1071.99, 1088, 3038.329565900004],
            #        [1515538800, 1065, 1098.5, 1071.99, 1088, 3038.329565900004]]
            return self._getJson('products/{}/candles?start={}&end={}&granularity={}'.format(product_id,
                                                                                             startDate.isoformat(),
                                                                                             endDate.isoformat(),
                                                                                             granularity))

        print("Granularity {} is out of bounds, use a different time range".format(g))
        return []
