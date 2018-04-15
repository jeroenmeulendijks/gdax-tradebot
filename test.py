
from exchange.Orders import *
from config import *

import datetime
import asyncio

async def run_orderbook():
    async with gdax.orderbook.OrderBook(product_ids='BTC-EUR',
                                        api_key=API_KEY,
                                        api_secret=API_SECRET,
                                        passphrase=API_PASS) as orderbook:
        while True:
            message = await orderbook.handle_message()
            if message is None:
                continue
            print('BTC-EUR ask: %s bid: %s' %
                  (orderbook.get_ask('BTC-EUR'),
                   orderbook.get_bid('BTC-EUR')))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_orderbook())

exit(0)
# Test method to retrieve historic data from gdax
resultList = []
dayIncrease = 10
start = datetime.datetime(2018, 1, 1)
end = start + datetime.timedelta(days=dayIncrease)

while (end < datetime.datetime.now()):
    resultList += cb.getHistoricRates("LTC-EUR", start, end)
    start = end
    end += datetime.timedelta(days=dayIncrease)

print(resultList)
