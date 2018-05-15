
import datetime
from calendar import timegm
import time
import pandas as pd
import os.path

from stockstats import StockDataFrame
from math import pi

from config import *

if (PLOT == 1):
    from mpl_finance import candlestick2_ohlc
    import matplotlib
    # Select different backend otherwise the window will keep popping in front while plotting new data
    #['GTK', 'GTKAgg', 'GTKCairo', 'GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg',
    # 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo',
    # 'agg', 'cairo', 'gdk', 'pdf', 'pgf', 'ps', 'svg', 'template']
    matplotlib.use('WXagg')

    import matplotlib.pyplot as plt

from exchange.OHLC import *
from model.Indicators import *

class Model(object):
    def __init__(self, productId, callback, *args, **kwargs):
        self.csv_price = "price_{}.csv".format(productId)
        self.figureIndex = None
        self.productId = productId
        self.callback = callback

        # Setup the indicator classes
        self.indicators = []
        for indicatorClass in Indicator.__subclasses__():
            if (indicatorClass.isEnabled()):
                self.indicators.append(indicatorClass())

        # Create dataframe to store data
        self.ema_dataframe = pd.DataFrame(data={'datetime': [],
                                                'epoch': [],
                                                'open': [],
                                                'close': [],
                                                'high': [],
                                                'low': [],
                                                'volume': [],
                                                'signal': []})

        # Add headers to CSV if don't exist
        csv_price_exists = os.path.isfile(self.csv_price)
        #if not csv_price_exists:
        self.logPrice(False)

    def addCandle(self, ohlc):
        utc_time = time.strptime(ohlc.getTime(), "%Y-%m-%dT%H:%M:%S.%fZ")
        epoch_time = timegm(utc_time)

        df = pd.DataFrame({'datetime': ohlc.getTime(),
                           'epoch': epoch_time,
                           'open': ohlc.getOpen(),
                           'close': ohlc.getClose(),
                           'high': ohlc.getHigh(),
                           'low': ohlc.getLow(),
                           'volume': ohlc.getVolume()
                          }, index=[0])

        self.ema_dataframe = self.ema_dataframe.append(df, ignore_index=True)

        self.logPrice()

        dfCopy = self.ema_dataframe.copy(True)
        stock = StockDataFrame.retype(dfCopy)

        for indicator in self.indicators:
            signal = indicator.signal(stock)
            if (signal.value != None):
                if (signal.value == Signal.BUY):
                    self.callback({'value': 'buy', 'productId': self.productId, 'price': ohlc.getClose()})
                if (signal.value == Signal.SELL):
                    self.callback({'value': 'sell', 'productId': self.productId, 'price': ohlc.getClose()})
                break

    def plotGraph(self):
        # Plot X/Y graph for both EMAs, with a movin window
        df = self.ema_dataframe.tail(50)
        length = df.shape[0]
        if length > 1:
            dfCopy = df.copy(True)
            stock = StockDataFrame.retype(dfCopy)

            if (self.figureIndex == None):
                self.figureIndex = len(plt.get_fignums()) + 1
            numRows = len(self.indicators) + 1
            for indicator in self.indicators:
                if (indicator.plotWithPrice()):
                    numRows -= 1

            plt.figure(self.figureIndex, figsize=(20, 12), dpi=60)
            pricePlot = plt.subplot(numRows, 1, 1)
            pricePlot.cla()
            ax = plt.gca()
            ax.set_title(self.productId)
            ax.set_xticklabels([])
            candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.4, colorup='#77d879', colordown='#db3f3f')
            plt.ylabel('Price')

            plotIndex = 2
            for indicator in self.indicators:
                if (indicator.plotWithPrice()):
                    p = pricePlot
                else:
                    p = plt.subplot(numRows, 1, plotIndex)
                    plotIndex += 1
                indicator.plot(p, stock)

                plt.ylabel(indicator)
                plt.legend()

            plt.pause(0.05)

    def logPrice(self, append = True):
        mode='w'
        if (append):
            mode = 'a'
        self.ema_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', mode=mode, index=False, header=not append)
