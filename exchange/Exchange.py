import json, requests, datetime

class Exchange(object):
    # Abstraction class to buy/sell on an exchange (ex. gdax)

    def __init__(self, exchange):
        # exchange: low-level interface to exchange
        self.cb = exchange

    def getObject(self, product_id):
        return self.cb.getObject(product_id)

    def getTime(self):
        return datetime.datetime.fromtimestamp(self.cb.getTime()).strftime('%Y-%m-%d %H:%M:%S')

    def getBalance(self, currency):
        return self.cb.getBalance(currency)

    def getProductId(self, base_currency, quote_currency):
        return self.cb.getProductId(base_currency, quote_currency)

    def getPrice(self, product_id):
        return self.cb.getPrice(product_id)

    def getOrderStatus(self, order_id):
        return self.cb.getOrderStatus(order_id)

    def buy(self, product_id, base_currency):
        # Buy cryptocurrency and return order information
        price = self.cb.determinePrice(product_id, 'buy')
        balance = self.cb.getBalance(base_currency) * 0.1
        quantity = balance / price

        return self._executeTrade("buy", product_id, quantity, price)

    def sell(self, product_id, quote_currency, base_currency):
        # Sell cryptocurrency and return order information
        price = self.cb.determinePrice(product_id, 'sell')
        quantity = self.cb.getBalance(quote_currency)

        return self._executeTrade("sell", product_id, quantity, price)

    def sellUpper(self, product_id, quote_currency, price, base_currency):
        # Create limit sell order cryptocurrency and return order information
        sell_price = float(price) * 1.003 # Limit profit at 0.3%
        quantity = self.cb.getBalance(quote_currency)

        return self._executeTrade("sellUpper", product_id, quantity, sell_price)

    def _executeTrade(self, type, product_id, quantity, price):
        order = self._createEmptyOrderResult()

        if (quantity > 0):
            if (type == "sellUpper"):
                res = self.cb.sell(product_id, quantity, price, True)
            elif (type == "sell"):
                res = self.cb.sell(product_id, quantity, price, False)
            elif (type == "buy"):
                res = self.cb.buy(product_id, quantity, price)

            if ('id' in res):
                order = res
                self.logTransaction(order)
            else:
                print (res['message'])
        else:
            print("No quantity available for trade")

        return order

    def cancelOrder(self, order_id):
        result = self.cb.cancelOrder(order_id)
        if 'message' in result:
            print("Cancel order result: {}".format(result['message']))
            return False
        else:
            return True

    def cancelOpenOrders(self):
        self.cb.cancelOpenOrders()

    def _createEmptyOrderResult(self):
        order = {}
        order['side'] = ''
        order['id'] = ''
        order['product_id'] = ''
        order['price'] = ''
        order['size'] = ''
        order['status'] = 'not started'
        return order

    def logTransaction(self, order):
        time = self.getTime()
        print ("{} {} Order: {} Product-id: {} Price: {} Quantity: {} Status: {}".format(time,
                                                                               order['side'],
                                                                               order['id'],
                                                                               order['product_id'],
                                                                               order['price'],
                                                                               order['size'],
                                                                               order['status']))
