import asyncio
import aiohttp
import random
import time
import uuid
import logging
import math

from threading import Thread
from queue import Queue

from config import *
from exchange.GdaxTrader import *

# Worker Queue for orders
tradeQueue = Queue()
logger = logging.getLogger('gdax-tradebot')

def worker():
    while True:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        trader, order = tradeQueue.get()
        loop.run_until_complete(handle_order(trader, order))
        loop.close()
        tradeQueue.task_done()

async def handle_order(trader, order):
    #trader = getTrader()
    starttime = time.time()

    logger.info("{}".format(order))

    try:
        if (order.type == "sell"):
            res = await trader.sell(type='limit', product_id=order.productId, size=order.size, price=order.price, time_in_force='GTC')
        else: # Buy
            res = await trader.buy(type='limit', product_id=order.productId, size=order.size, price=order.price, time_in_force='GTC')
        order.update(res)

    except aiohttp.client_exceptions.ClientResponseError as e:
        logger.error('Failed to execute [{}] Error: {}'.format(order, e))
        # Set order done with error state
        order.update({'status': 'done', 'done_reason': e})

    # Wait until the order is finished
    while (order.status != 'done'):
        # Randomly wait some time before (re)trying again
        await asyncio.sleep(random.uniform(1, 5))

        try:
            stat = await trader.get_order(order.id)
            order.update(stat)
            logger.debug("Order: {} has status {}".format(order.id, order.status))
        except aiohttp.client_exceptions.ClientResponseError as e:
            logger.error('Failed to execute [{}] Error: {}'.format(order, e))
            break

        if ((time.time() - starttime) > order.timeout):
            logger.info("Order {} has timedout. Cancelling the order".format(order.id))
            # TODO: Not sure why but cancel_order(order_id) fails with bad_request, so for now cancel all orders
            #stat = await trader.cancel_order(order.id)
            stat = await trader.cancel_all()
            # TODO: Check if order really cancelled
            #print(stat)
            break

    logger.debug("DONE HANDLING ORDER: {}".format(order))

class Order(object):
    def __init__(self, type, productId, size, price):
        self.type = type
        self.productId = productId
        self.size = size
        self.price = price
        self.clientOid = uuid.uuid4()
        self.timeout = ORDER_TIMEOUT

        # Status/Result of the order
        self.id = ''
        self.status = 'unknown'
        self.done_reason = ''
        self.filled_size = 0

    def update(self, result):
        if('id' in result):
            self.id = result['id']
        if('status' in result):
            self.status = result['status']
        if('done_reason' in result):
            self.done_reason = result['done_reason']
        if('filled_size' in result):
            self.filled_size = result['filled_size']

    def __str__(self):
        if (self.status == "done"):
            return("{} [{}] Size: {} Filled: {} Reason: {}".format(self.type, self.clientOid, self.size, self.filled_size, self.done_reason))
        else:
            return ("{} [{}] {} size: {} price: {}".format(self.type, self.clientOid, self.productId, self.size, self.price))

class OrderManager(object):
    def __init__(self):
        self.trader = getTrader()
        self.products = {}
        self.accounts = {}
        self.orders = []

        # Create a ThreadPool for handling orders
        for i in range(5):
            t = Thread(target=worker)
            t.daemon = True
            t.start()

    async def initialize(self):
        # Get quote / min / max
        products = await self.trader.get_products()
        logger.debug(products)
        for prod in products:
            self.products[prod['id']] = { 'quote_increment': float(prod['quote_increment']),
                                          'base_min_size': float(prod['base_min_size']),
                                          'base_max_size': float(prod['base_max_size']) }
        # Get accounts
        accounts = await self.trader.get_account()
        logger.debug(accounts)
        for account in accounts:
            self.accounts[account['currency']] = account['id']

    async def buy(self, productId, currentPrice):
        crypto, currency = productId.split("-")

        balance = await self.getBalance(currency)
        volume = self.getVolume(productId, (balance / currentPrice))
        price = self.getPrice(productId, currentPrice)

        if (volume > 0.0):
            order = Order('buy', productId, volume, price)
            self.orders.append(order)

            tradeQueue.put((self.trader, order))

            return order.clientOid
        else:
            logger.error("Not enough balance to execute [buy] order. Balance: {} Volume: {} Price: {}".format(balance, volume, price))
        return -1

    async def sell(self, productId, currentPrice):
        crypto, currency = productId.split("-")

        volume = await self.getBalance(crypto)
        price = self.getPrice(productId, currentPrice)

        if (volume > 0.0):
            order = Order('sell', productId, volume, price)
            self.orders.append(order)

            tradeQueue.put((self.trader, order))

            return order.clientOid
        else:
            logger.error("Not enough balance to execute [sell] order. Balance: {} Price: {}".format(volume, price))
        return -1

    def getOrders(self):
        return self.orders

    async def getBalance(self, currency):
        accounts = await self.trader.get_account(self.accounts[currency])
        return float(accounts['available'])

    def getVolume(self, productId, amount):
        quote = self.products[productId]['quote_increment']
        base_min_size = self.products[productId]['base_min_size']
        base_max_size = self.products[productId]['base_max_size']

        # Make sure we always have a multiple of the quote value for the volume
        volume = quote * math.floor(amount / quote)

        # Volume must be between base_min_size and base_max_size
        if (volume < base_min_size): volume = 0
        if (volume > base_max_size): volume = base_max_size

        return volume

    def getPrice(self, productId, price):
        quote = self.products[productId]['quote_increment']

        return (quote * math.floor(price / quote))