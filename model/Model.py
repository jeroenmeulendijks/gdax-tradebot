
from datetime import datetime
import pandas as pd
import os.path
import matplotlib.pyplot as plt

class Model(object):
    def __init__(self, csv_prices):
        # Create CSV files for logging price and transactions
        self.csv_price = csv_prices

        # Create dataframes to store data
        self.ema_dataframe = pd.DataFrame(data={'datetime': [],'price': [], 'EMA5': [], 'EMA20': [], 'RSI': [], 'signal': []})

        # Add headers to CSV if don't exist
        csv_price_exists = os.path.isfile(self.csv_price)
        #if not csv_price_exists:
        self.logPrice(False)

    def addPrice(self, datetime, price):
        # Get current price and time and add to dataframe
        self.ema_dataframe = self.ema_dataframe.append(pd.DataFrame({'datetime': datetime, 'price': price}, index=[0]), ignore_index=True)
        length = self.ema_dataframe.shape[0]
        if (length > 5):
            self.ema_dataframe['EMA5'] = self.ema_dataframe['price'].dropna().shift().fillna(self.ema_dataframe['EMA5']).ewm(com=5).mean()
        if (length > 20):
            self.ema_dataframe['EMA20'] = self.ema_dataframe['price'].dropna().shift().fillna(self.ema_dataframe['EMA20']).ewm(com=20).mean()

    def calculateRSI(self, period):
        # Calculate RSI and add to dataframe
        length = self.ema_dataframe.shape[0]
        if (length > period):
            delta = self.ema_dataframe['price'].dropna().apply(float).diff()
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
                signal = {'signal': True, 'value': 'sell'}
            elif (EMA5[1] >= EMA20[1]) & (EMA5[0] <= EMA20[0]):
                signal = {'signal': True, 'value': 'buy'}

            self.ema_dataframe.loc[self.ema_dataframe.index[length-1], 'signal'] = signal['value']

        self.logPrice()
        return signal

    def plotGraph(self):
        # Plot X/Y graph for both EMAs, with a movin window
        df = self.ema_dataframe.tail(50)
        length = df.shape[0]
        if length > 1:
            plt.clf()
            plt.plot(df['datetime'], df['price'])
            plt.plot(df['datetime'], df['EMA5'])
            plt.plot(df['datetime'], df['EMA20'])
            plt.xlabel('Datetime')
            plt.ylabel('Price')
            plt.legend()
            plt.gca().relim()
            plt.gca().autoscale_view()
            plt.pause(0.05)

    def logPrice(self, append = True):
        mode='w'
        if (append):
            mode = 'a'
        self.ema_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', mode=mode, index=False, header=not append)
