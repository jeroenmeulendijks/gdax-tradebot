
from exchange.CoinBase import *
from exchange.Exchange import *
from config import *

import datetime

cb = Coinbase(API_KEY, API_SECRET, API_PASS, API_URL)
#e = Exchange(cb)

#e.buy("ETH-EUR", "EUR")

#print (cb.getTime())
#print (cb.getBalance("EUR"))
#print (cb.getBalance("ETH"))
#print (cb.getProductId("ETH", "EUR"))
#print (cb.buy("ETH-EUR", 1, 0.99))

#print (cb.getOrderStatus("30082361-c34a-4369-a792-1666dbfb6462"))
#print (cb.getOrderStatus("10"))
#print (cb.getOrders())

#print(e.cancelOrder("705171a8-9611-4e28-a5c5-f346dd5be616"))
#print (cb.getOrders())

#print(cb.determinePrice("ETH-EUR", "buy"))

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
