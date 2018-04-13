import time
from threading import Event, Thread
from exchange.CoinBase import *
from exchange.DemoCoinBase import *
from exchange.Exchange import *
from model.Model import *
from config import *

class TimedThread(Thread):
    # Class used to log price, calculate EMA & Crossover and then trigger a separate thread to
    # buy/sell the chosen cryptocurrency
    def __init__(self, event, wait_time, quote_currency, base_currency, csv_price):
        Thread.__init__(self)
        self.stopped = event
        self.wait_time = wait_time
        self.quote_currency = quote_currency
        self.base_currency = base_currency
        self.order_timeout = 900 # 15 minutes (in seconds)

        if (TEST_MODE):
            cb = DemoCoinBase(API_KEY, API_SECRET, API_PASS, API_URL)
        else:
            cb = Coinbase(API_KEY, API_SECRET, API_PASS, API_URL)
        self.model = Model(csv_price)
        self.exchange = Exchange(cb)

        self.product_id = self.exchange.getProductId(self.quote_currency, self.base_currency)

    def getModel(self):
        return self.model

    def run(self):
        # Run thread until stopped by 'stopFlag' Event, waiting at set intervals
        while not self.stopped.wait(self.wait_time):
            signal = self.EMACrossover()
            if signal is not None:
                if signal['value'] == 'buy':
                    self.order('buy')
                    #order_thread = Thread(target=self.order, args=('buy',))
                    #order_thread.daemon = True
                    #order_thread.start()
                elif signal['value'] == 'sell':
                    self.order('sell')
                    #order_thread = Thread(target=self.order, args=('sell',))
                    #order_thread.daemon = True
                    #order_thread.start()
            else:
                print("EMACrossover calculate NO signal")

    def order(self, type):
        # Create order (sell/buy)
        if (type == 'sell'):
            self.exchange.cancelOpenOrders()

        if (type == 'sell'):
            order = self.exchange.sell(self.product_id, self.quote_currency, self.base_currency)
        else:
            order = self.exchange.buy(self.product_id, self.base_currency)

        order_id = order['id']

        timer_count = 0
        while True:
            # Cancel order if timeout
            if (timer_count > self.order_timeout):
                self.exchange.cancelOrder(order_id)
                print('Time: {}, Time limit exceeded, order cancelled'.format(self.exchange.getTime()))
                break

            order_status = self.exchange.getOrderStatus(order_id)

            if (order_status == 'done'):
                print('Time: {}, {} fulfilled'.format(self.exchange.getTime(), order['id']))

                # Set upperlimit when price is increased enough
                #if (type == 'buy'):
                #    upper_order = self.exchange.sellUpper(self.product_id, self.quote_currency, order['price'], self.base_currency)
                #    # TODO: Handle when setting sell order failed?!
                break
            time.sleep(1)
            timer_count = timer_count + 1

    def EMACrossover(self):
        # Trigger order function on separate thread if EMA crossover detected & RSI within threshold
        self.model.addPrice(self.exchange.getTime(), self.exchange.getPrice(self.product_id))
        self.model.add(self.exchange.getObject(self.product_id))
        return self.model.calculateCrossover()
