import pandas as pd
import matplotlib.pyplot as plt

from config import *

from stockstats import StockDataFrame
from abc import ABC, abstractmethod

class Signal(object):
    BUY = "BUY"
    SELL = "SELL"

    value = None

class Indicator(ABC):

    def __init__(self):
        super().__init__()

    def plotWithPrice(self):
        # We assume that an indicator will not be plotted together with the prices
        # when you want to plot the indicator with the prices override this method
        # and return True
        return False

    @abstractmethod
    def plot(self, subplot, stock):
        pass

    def signal(self, dataframes):
        return Signal()

    @classmethod
    def isEnabled(cls):
        return (cls.__str__(cls) in INDICATORS)

    @abstractmethod
    def __str__(self):
        pass

class EMA(Indicator):

    def __init__(self):
        super().__init__()

    def plotWithPrice(self):
        return True

    def plot(self, subplot, stock):
        plt.plot(stock['datetime'], stock['close_5_ema'])
        plt.plot(stock['datetime'], stock['close_20_ema'])

    def signal(self, stock):
        s = Signal()
        if stock.shape[0] > 5:
            EMA5 = stock['close_5_ema'].tail(2).reset_index(drop=True)
            EMA20 = stock['close_20_ema'].tail(2).reset_index(drop=True)
            if (EMA5[1] <= EMA20[1]) & (EMA5[0] >= EMA20[0]):
                 s.value = Signal.SELL
            elif (EMA5[1] >= EMA20[1]) & (EMA5[0] <= EMA20[0]):
                s.value = Signal.BUY

        return s

    def __str__(self):
        return "EMA"

class RSI(Indicator):

    def __init__(self):
        super().__init__()

    def plot(self, subplot, stock):
        subplot.cla()
        plt.plot(stock['datetime'], stock['rsi_14'])

    def __str__(self):
        return "RSI"

    def calculateRSI(self, dataframe, period):
        # Calculate RSI and add to dataframe
        length = dataframe.shape[0]

        if (length >= period):
            delta = dataframe['close'].dropna().apply(float).diff()
            dUp, dDown = delta.copy(), delta.copy()
            dUp[dUp < 0] = 0
            dDown[dDown > 0] = 0
            RollUp = dUp.rolling(window=period).mean()
            RollDown = dDown.rolling(window=period).mean().abs()
            RS = RollUp / RollDown
            RSI = 100.0 - (100.0 / (1.0 + RS))
            dataframe['RSI'] = RSI

class MACD(Indicator):

    def __init__(self):
        super().__init__()

    def plot(self, subplot, stock):
        subplot.cla()
        plt.plot(stock['datetime'], stock['macd'])
        plt.plot(stock['datetime'], stock['macds'])

    def signal(self, stock):
        s = Signal()
        if stock.shape[0] > 2:
            signal = stock['macds'].tail(2).reset_index(drop=True)
            macd = stock['macd'].tail(2).reset_index(drop=True)

            # If the MACD crosses the signal line upward BUY!
            if macd[1] > signal[1] and macd[0] <= signal[0]:
                s.value = Signal.BUY
            # The other way around. SELL
            elif macd[1] < signal[1] and macd[0] >= signal[0]:
                s.value = Signal.SELL
            # Do nothing if not crossed
            else:
                pass

        return s

    def __str__(self):
        return "MACD"

class DMI(Indicator):

    def __init__(self):
        super().__init__()

    def plot(self, subplot, stock):
        subplot.cla()
        # +DI, default to 14 days
        plt.plot(stock['datetime'], stock['pdi'])
        # -DI, default to 14 days
        plt.plot(stock['datetime'], stock['mdi'])
        plt.plot(stock['datetime'], stock['adx'])
        plt.plot(stock['datetime'], stock['adxr'])

    def __str__(self):
        return "DMI"