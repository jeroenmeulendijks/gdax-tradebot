import threading
import time
import datetime
import logging

class RepeatingTimer(object):
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = threading.Timer(self.interval, self.callback)
        self.timer.setDaemon(True)
        self.timer.start()

class OHLC(object):

    def __init__(self, periodInSeconds, productId, callback):
        self.prices = []
        self.sizes = []
        self.productId = productId
        self.lastestTime = datetime.datetime.now().isoformat()
        self.callback = callback
        self.logger = logging.getLogger('gdax-tradebot')

        self.t = RepeatingTimer(periodInSeconds, self.timeExpired)
        self.t.start()

    def __del__(self):
        self.t.cancel()

    def add(self, message):
        if message is not None and message['type'] == 'match' and message['product_id'] == self.getProductId():
            self.prices.append(float(message['price']))
            self.sizes.append(float(message['size']))
            self.lastestTime = message['time']

    def getTime(self):
        return self.lastestTime

    def getProductId(self):
        return self.productId

    def getOpen(self):
        return next(iter(self.prices), "-")

    def getClose(self):
        return next(reversed(self.prices), "-")

    def getHigh(self):
        return max(self.prices, default='-')

    def getLow(self):
        return min(self.prices, default='-')

    def getVolume(self):
        return sum(self.sizes)

    def timeExpired(self):
        self.logger.info(self)
        if (len(self.prices) > 0):
            self.callback(self)
        del self.prices[:]
        del self.sizes[:]

    def __str__(self):
        return "{} O: {} H: {} L: {} C: {} V: {} {}".format(self.getProductId(),
                                                            self.getOpen(),
                                                            self.getHigh(),
                                                            self.getLow(),
                                                            self.getClose(),
                                                            self.getVolume(),
                                                            'UP' if self.getOpen() < self.getClose() else 'DOWN')