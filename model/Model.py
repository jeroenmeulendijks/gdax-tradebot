
import datetime
from calendar import timegm
import time
import pandas as pd
import os.path

from stockstats import StockDataFrame
from math import pi
from mpl_finance import candlestick2_ohlc

from exchange.OHLC import *
from config import *

if (PLOT == 1):
    import matplotlib
    # Select different backend otherwise the window will keep popping in front while plotting new data
    #['GTK', 'GTKAgg', 'GTKCairo', 'GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg',
    # 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo',
    # 'agg', 'cairo', 'gdk', 'pdf', 'pgf', 'ps', 'svg', 'template']
    matplotlib.use('WXagg')

    import matplotlib.pyplot as plt

class Model(object):
    def __init__(self, productId, ohlcQueue, candleTimeInsec, callback, *args, **kwargs):
        self.csv_price = "price_{}.csv".format(productId)
        self.figureIndex = None
        self.productId = productId
        self.ohlcQueue = ohlcQueue
        self.ohlc = OHLC(candleTimeInsec, productId, self._newCandleAvailable)
        self.callback = callback

        # Create dataframe to store data
        self.ema_dataframe = pd.DataFrame(data={'datetime': [],
                                                'epoch': [],
                                                'open': [],
                                                'close': [],
                                                'high': [],
                                                'low': [],
                                                'volume': [],
                                                'signal': []})
        #self.ema_dataframe = pd.DataFrame(data={'datetime': [],
        #                                        'epoch': [],
        #                                        'open': [],
        #                                        'close': [],
        #                                        'high': [],
        #                                        'low': [],
        #                                        'volume': [],
        #                                        'EMA5': [],
        #                                        'EMA20': [],
        #                                        'RSI': [],
        #                                        'signal': []})

        # Add headers to CSV if don't exist
        csv_price_exists = os.path.isfile(self.csv_price)
        #if not csv_price_exists:
        self.logPrice(False)

    def add(self, message):
        self.ohlc.add(message)

    def calculateRSI(self, period):
        # Calculate RSI and add to dataframe
        length = self.ema_dataframe.shape[0]

        if (length >= period):
            delta = self.ema_dataframe['close'].dropna().apply(float).diff()
            dUp, dDown = delta.copy(), delta.copy()
            dUp[dUp < 0] = 0
            dDown[dDown > 0] = 0
            RollUp = dUp.rolling(window=period).mean()
            RollDown = dDown.rolling(window=period).mean().abs()
            RS = RollUp / RollDown
            RSI = 100.0 - (100.0 / (1.0 + RS))
            self.ema_dataframe['RSI'] = RSI

    def calculateCrossover(self):
        # Calculate EMA crossover and return signal
        signal = {'signal': False, 'value': None}
        length = self.ema_dataframe.shape[0]
        if (length > 5):
            EMA5 = self.ema_dataframe['EMA5'].tail(2).reset_index(drop=True)
            EMA20 = self.ema_dataframe['EMA20'].tail(2).reset_index(drop=True)
            if (EMA5[1] <= EMA20[1]) & (EMA5[0] >= EMA20[0]):
                signal = {'signal': True, 'value': 'sell', 'productId': self.productId}
            elif (EMA5[1] >= EMA20[1]) & (EMA5[0] <= EMA20[0]):
                signal = {'signal': True, 'value': 'buy', 'productId': self.productId}

            self.ema_dataframe.loc[self.ema_dataframe.index[length-1], 'signal'] = signal['value']

        self.logPrice()
        return signal

    def _newCandleAvailable(self, ohlc):
        self.ohlcQueue.put(ohlc)

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
        length = self.ema_dataframe.shape[0]

        #if (length >= 5):
        #    self.ema_dataframe['EMA5'] = self.ema_dataframe['close'].dropna().shift().fillna(self.ema_dataframe['EMA5']).ewm(com=5, min_periods=4).mean()

        #if (length >= 20):
        #    self.ema_dataframe['EMA20'] = self.ema_dataframe['close'].dropna().shift().fillna(self.ema_dataframe['EMA20']).ewm(com=20, min_periods=19).mean()

        #self.calculateRSI(14)

        #signal = self.calculateCrossover()
        #if (signal is not None) and ((signal['value'] == 'buy') or (signal['value'] == 'sell')):
        #    self.callback(signal)

    def plotGraph(self):
        # Plot X/Y graph for both EMAs, with a movin window
        if (PLOT == 1):
            df = self.ema_dataframe.tail(50)
            length = df.shape[0]
            if length > 1:
                dfCopy = df.copy(True)
                stock = StockDataFrame.retype(dfCopy)

                signal = stock['macds']        # Your signal line
                macd   = stock['macd']         # The MACD that need to cross the signal line to give you a Buy/Sell signal

                #for i in range(1, len(signal)):
                #    # If the MACD crosses the signal line upward BUY!
                #    if macd[i] > signal[i] and macd[i - 1] <= signal[i - 1]:
                #        listLongShort.append("BUY")
                #    # The other way around. SELL
                #    elif macd[i] < signal[i] and macd[i - 1] >= signal[i - 1]:
                #        listLongShort.append("SELL")
                #    # Do nothing if not crossed
                #    else:
                #        listLongShort.append("HOLD")

                if (self.figureIndex == None):
                    self.figureIndex = len(plt.get_fignums()) + 1
                numRows = len(INDICATORS) + 1

                plt.figure(self.figureIndex, figsize=(20, 12), dpi=60)
                p = plt.subplot(numRows, 1, 1)
                p.cla()
                ax = plt.gca()
                ax.set_title(self.productId)
                ax.set_xticklabels([])
                candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.4, colorup='#77d879', colordown='#db3f3f')
                plt.ylabel('Price')

                for i, indicator in enumerate(INDICATORS):
                    p = plt.subplot(numRows, 1, i + 2)
                    p.cla()
                    if (indicator == 'MACD'):
                        plt.plot(df['datetime'], macd)
                        plt.plot(df['datetime'], signal)
                    if (indicator == 'RSI'):
                        plt.plot(df['datetime'], stock['rsi_14'])
                    if (indicator == 'DMI'):
                        # +DI, default to 14 days
                        plt.plot(df['datetime'], stock['pdi'])
                        # -DI, default to 14 days
                        plt.plot(df['datetime'], stock['mdi'])
                    if (indicator == 'EMA'):
                        #plt.plot(df['datetime'], df['EMA5'])
                        #plt.plot(df['datetime'], df['EMA20'])
                        plt.plot(df['datetime'], stock['close_5_ema'])
                        plt.plot(df['datetime'], stock['close_20_ema'])
                    plt.ylabel(indicator)
                    plt.legend()

                plt.pause(0.05)

    def logPrice(self, append = True):
        mode='w'
        if (append):
            mode = 'a'
        self.ema_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', mode=mode, index=False, header=not append)
