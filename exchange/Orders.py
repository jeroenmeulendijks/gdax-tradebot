import asyncio
import aiohttp
import gdax
import random
import time
import uuid

from threading import Thread
from queue import Queue

from config import *

# Worker Queue for orders
q = Queue()

def worker():
    while True:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        order = q.get()
        loop.run_until_complete(handle_order(order))
        loop.close()
        q.task_done()

async def handle_order(order):
    trader = gdax.trader.Trader(product_id=order['productId'], api_key=API_KEY, api_secret=API_SECRET, passphrase=API_PASS)
    starttime = time.time()
    status = 'done'
    order_id = ''

    if (order['type'] == "sell"):
        try:
            res = await trader.sell(type='limit', size=order['size'], price=order['price'], time_in_force='GTC')
            # TODO: check if the result has 'id'?!
            order_id = res['id']
            status = res['status']
        except aiohttp.client_exceptions.ClientResponseError as e:
            print('Failed to execute [sell] order: {} Error: {}'.format(order['client_oid'], e))
    else: # buy
        try:
            res = await trader.buy(type='limit', size=order['size'], price=order['price'], time_in_force='GTC')
            # TODO: check if the result has 'id'?!
            order_id = res['id']
            status = res['status']
        except aiohttp.client_exceptions.ClientResponseError as e:
            print('Failed to execute [buy] order: {} Error: {}'.format(order['client_oid'], e))

    # Wait until the order is finished
    while (status != 'done'):
        # Randomly wait some time before (re)trying again
        await asyncio.sleep(random.uniform(1, 5))

        try:
            stat = await trader.get_order(order_id)
            status = stat['status']
            #print("Order: {} has status {}".format(order_id, status))
        except aiohttp.client_exceptions.ClientResponseError as e:
            print(e)
            break

        if (order['timeout'] > 0 and (time.time() - starttime) > order['timeout']):
            print("Order {} has timedout. Cancelling the order".format(order_id))
            # TODO: Not sure why but cancel_order(order_id) fails with bad_request, so for now cancel all orders
            #stat = await trader.cancel_order(order_id)
            stat = await trader.cancel_all()
            # TODO: Check if order really cancelled
            #print(stat)
            break

    print("DONE HANDLING ORDER:" + str(order_id))

class Orders(object):
    def __init__(self):
        self.timeout = 0

        # Create a ThreadPool for handling orders
        for i in range(5):
            t = Thread(target=worker)
            t.daemon = True
            t.start()

    def setTimeout(self, timeoutInSec):
        self.timeout = timeoutInSec

    async def buy(self, params):
        params['type'] = 'buy'
        params['timeout'] = self.timeout
        params['client_oid'] = uuid.uuid4()

        if not (TEST_MODE):
            q.put(params)

        print("Buying {} size: {} price: {} ({})".format(params['productId'], params['size'], params['price'], params['client_oid']))

        return params['client_oid']

    async def sell(self, params):
        params['type'] = 'sell'
        params['timeout'] = self.timeout
        params['client_oid'] = uuid.uuid4()

        if not (TEST_MODE):
            q.put(params)

        print("Selling {} size: {} price: {} ({})".format(params['productId'], params['size'], params['price'], params['client_oid']))

        return params['client_oid']
