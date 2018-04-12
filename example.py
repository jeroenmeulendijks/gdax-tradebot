import time
from model.TimedThread import *

# Custom settings
LOOP_DURATION = 60 # Time period (in seconds)
MAX_LOOP_TIME = 120 # 10 * 60 * 60 # Max duration to run (in seconds)
QUOTE_CURRENCY = "BTC" # Cryptocurrency of choice
BASE_CURRENCY = "EUR" # Fiat currency of choice
CSV_PRICE = "price.csv" # Price CSV name

#Start thread
stopFlag = Event()
thread = TimedThread(stopFlag, LOOP_DURATION, QUOTE_CURRENCY, BASE_CURRENCY, CSV_PRICE)
thread.daemon = True
thread.start()

#Set max time to run
#time.sleep(MAX_LOOP_TIME)
timer_count = 0
while True:
    if (timer_count >= MAX_LOOP_TIME):
        break
    thread.getModel().plotGraph();
    time.sleep(LOOP_DURATION/4)
    timer_count += 1

stopFlag.set()

input("Press [enter] to continue.")