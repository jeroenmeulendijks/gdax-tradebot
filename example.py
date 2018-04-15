import time
import asyncio
import gdax

from exchange.DemoCoinBase import *
from exchange.Orders import *
from model.Model import *

# Custom settings
LOOP_DURATION = 10 # Time period (in seconds)
MAX_LOOP_TIME = 120 # 10 * 60 * 60 # Max duration to run (in seconds)
QUOTE_CURRENCY = "BTC" # Cryptocurrency of choice
BASE_CURRENCY = "EUR" # Fiat currency of choice
CSV_PRICE = "price.csv" # Price CSV name

PRODUCT_ID = "{}-{}".format(QUOTE_CURRENCY, BASE_CURRENCY)

orders = Orders()
orders.setTimeout(15)

model = Model(CSV_PRICE)

async def EMACrossover(trader):
    # Trigger order function on separate thread if EMA crossover detected & RSI within threshold
    ticker = await trader.get_product_ticker()
    time = await trader.get_time()

    model.addPrice(time['iso'], ticker['price'])
    return model.calculateCrossover()

async def worker():
    if (USE_TEST_PRICES):
        trader = DemoCoinBase(PRODUCT_ID)
    else:
        trader = gdax.trader.Trader(product_id=PRODUCT_ID, api_key=API_KEY, api_secret=API_SECRET, passphrase=API_PASS)

    while True:
        signal = await EMACrossover(trader)
        print(signal)
        if signal is not None:
            # TODO: Determine what to buy/sell (is now hard-coded!)
            if signal['value'] == 'buy':
                await orders.buy({'productId': 'BTC-EUR', 'size': 0.02, 'price': 1.00})
            elif signal['value'] == 'sell':
                await orders.sell({'productId': 'BTC-EUR', 'size': 0.001, 'price': 100000.00})
        else:
            print("EMACrossover calculate NO signal")

        # Enable to get a graph with values plotted
        #model.plotGraph();

        await asyncio.sleep(LOOP_DURATION)

loop = asyncio.get_event_loop()
loop.run_until_complete(worker())
