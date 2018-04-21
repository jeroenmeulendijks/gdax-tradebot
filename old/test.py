
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
