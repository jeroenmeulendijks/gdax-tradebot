import asyncio
import logging
import time
import queue

from exchange.Orders import *
from exchange.GdaxOrderBook import *
from model.Model import *
from config import *

import threading

def tradeSignalReceived(signal):
    tradeQueue.put(signal)

async def runTrader():
    manager = OrderManager()
    await manager.initialize()

    while True:
        signal = tradeQueue.get()
        logger.debug("Trade signal ({}) received for {}".format(signal['value'], signal['productId']))

        if signal['value'] == 'buy':
            await manager.buy(signal['productId'], signal['price'])
        elif signal['value'] == 'sell':
            await manager.sell(signal['productId'], signal['price'])

def newCandle(ohlc, productId):
    models[productId].addCandle(ohlc)
    plotQueue.put(ohlc)

async def runOrderBook():
    async with getOrderbook() as orderbook:
        while True:
            message = await orderbook.handle_message()

            if message is not None and message['type'] == 'match':
                ohlcs[message['product_id']].add(message)

def startOrderBook():
    loopBook = asyncio.new_event_loop()
    loopBook.run_until_complete(runOrderBook())

def startTrader():
    loopTrader = asyncio.new_event_loop()
    loopTrader.run_until_complete(runTrader())

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

    # Create logger for the OHLC
    ohlclogger = logging.getLogger('gdax-tradebot.ohlc')
    fh = logging.FileHandler('ohlc.log')
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ohlclogger.addHandler(fh)

if __name__ == "__main__":
    logger = logging.getLogger('gdax-tradebot')
    setupLogging(logger)

    tradeQueue = queue.Queue()
    plotQueue = queue.Queue()

    models = {}
    ohlcs = {}
    for productId in PRODUCT_IDS:
        ohlcs[productId] = OHLC(CANDLE_TIME, productId, newCandle)
        models[productId] = Model(productId, tradeSignalReceived)

    t = threading.Thread(target=startOrderBook)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=startTrader)
    t.setDaemon(True)
    t.start()

    while True:
        ohlc = plotQueue.get()
        if (PLOT == 1):
            for key, model in models.items():
                model.plotGraph()
