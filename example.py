import asyncio
import gdax
import queue
import logging
import time

from exchange.Orders import *
from exchange.DemoOrderBook import *
from model.Model import *
from config import *

import threading

def tradeSignalReceived(signal):
    # TODO: Determine what to buy/sell (is now hard-coded!)
    logger.debug("Trade signal ({}) received for {}".format(signal['value'], signal['productId']))

    if signal['value'] == 'buy':
        orders.buy({'productId': signal['productId'], 'size': 0.02, 'price': 1.00})
    elif signal['value'] == 'sell':
        orders.sell({'productId': signal['productId'], 'size': 0.001, 'price': 100000.00})

async def run_orderbook():
    if (USE_TEST_PRICES):
        with DemoOrderBook(PRODUCT_IDS) as orderbook:
            while True:
                message = await orderbook.handle_message()

                for model in models:
                    model.add(message)
    else:
        async with gdax.orderbook.OrderBook(product_ids=PRODUCT_IDS,
                                            api_key=API_KEY,
                                            api_secret=API_SECRET,
                                            passphrase=API_PASS, use_heartbeat=True) as orderbook:
            while True:
                message = await orderbook.handle_message()

                for model in models:
                    model.add(message)

def start_async_stuff():
    loop.run_until_complete(run_orderbook())

def setupLogging(logger):
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('debug.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

if __name__ == "__main__":
    logger = logging.getLogger('gdax-tradebot')
    setupLogging(logger)

    ohlcQueue = queue.Queue()

    orders = Orders()
    orders.setTimeout(ORDER_TIMEOUT)
    models = []

    for productId in PRODUCT_IDS:
        models.append(Model(productId, ohlcQueue, CANDLE_TIME, tradeSignalReceived))

    loop = asyncio.get_event_loop()

    t = threading.Thread(target=start_async_stuff)
    t.setDaemon (True)
    t.start()

    # Test for plotting the candlesticks which must be done on the main thread
    while True:
        try:
            _ = ohlcQueue.get(timeout=5)

            for model in models:
                model.plotGraph()
        except queue.Empty:
            pass
