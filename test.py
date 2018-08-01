import asyncio
import logging
import time

from exchange.Orders import *

import threading

import paho.mqtt.client as mqtt

class Mqtt(object):
  BASE_DIR = '/home/pi/development/home-automation/cert'

  def __init__(self):
    self.callbackMethod = None

    self.client = mqtt.Client()
    #self.client.tls_set(self.BASE_DIR + '/ca.crt', self.BASE_DIR + '/client.crt', self.BASE_DIR + '/client.key')
    self.client.connect("192.168.0.204", 8883, 60)
    self.client.on_message = self._on_message

  def publish(self, topic, data):
    self.client.publish(topic, data)

  def subscribe(self, topic):
    self.client.subscribe(topic)

  def onMessage(self, method):
    self.callbackMethod = method

  def loopStart(self):
    self.client.loop_start()

  def loopForever(self):
    self.client.loop_forever()

  def _on_message(self, client, userdata, msg):
    if (self.callbackMethod):
      msg = msg.payload.decode('utf-8')
      self.callbackMethod(msg)

async def runTrader():
    manager = OrderManager()
    await manager.initialize()

    #await manager.buy(signal['productId'], signal['price'])
    #await manager.sell(signal['productId'], signal['price'])
    
    await manager.buy("BTC-EUR", 50.00)
    
    time.sleep(1)
    
    #m = Mqtt()
    #logger.info("Publish")
    #m.publish("gdax-trader/test", "Hello")

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
    
    loopTrader = asyncio.new_event_loop()
    loopTrader.run_until_complete(runTrader())
    
    #m = Mqtt()
    #m.publish("owntracks/test", "Hello")
    #m.subscribe("gdax-trader/#")
    #logger.info("Looping")
    #m.loopForever()
    
    