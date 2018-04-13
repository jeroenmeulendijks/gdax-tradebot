
from datetime import datetime
import pandas as pd
import os.path

from stockstats import StockDataFrame
from math import pi
from bokeh.plotting import figure, show, output_notebook, output_file
from bokeh.models import DatetimeTickFormatter

class Model(object):
    def __init__(self, csv_prices):
        # Create CSV files for logging price and transactions
        self.csv_price = csv_prices

        # Create dataframes to store data
        self.ema_dataframe = pd.DataFrame(data={'datetime': [],'price': [], 'EMA5': [], 'EMA20': [], 'RSI': [], 'signal': []})
        self.df = pd.DataFrame(data={'datetime': [],'open': [], 'high': [], 'low': [], 'close': [], 'volume': []})

        # Add headers to CSV if don't exist
        csv_price_exists = os.path.isfile(self.csv_price)
        #if not csv_price_exists:
        self.logPrice(False)

    def add(self, object):
        # [ time, low, high, open, close, volume ]
        time = datetime.fromtimestamp(object[0])
        self.df = self.df.append(pd.DataFrame({'datetime': time, 'low': object[1], 'high': object[2], 'open': object[3], 'close': object[4], 'volume': object[5]}, index=[0]), ignore_index=True)

    def addPrice(self, datetime, price):
        # Get current price and time and add to dataframe
        self.ema_dataframe = self.ema_dataframe.append(pd.DataFrame({'datetime': datetime, 'price': price}, index=[0]), ignore_index=True)
        length = self.ema_dataframe.shape[0]

        if (length >= 5):
            self.ema_dataframe['EMA5'] = self.ema_dataframe['price'].dropna().shift().fillna(self.ema_dataframe['EMA5']).ewm(com=5,min_periods=4).mean()

        if (length >= 20):
            self.ema_dataframe['EMA20'] = self.ema_dataframe['price'].dropna().shift().fillna(self.ema_dataframe['EMA20']).ewm(com=20,min_periods=19).mean()

        self.calculateRSI(14)

    def calculateRSI(self, period):
        # Calculate RSI and add to dataframe
        length = self.ema_dataframe.shape[0]

        if (length >= period):
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
            dfCopy = self.df.copy(True)
            stock = StockDataFrame.retype(dfCopy)
            #rsi = stock['rsi_14']
            ema5 = stock['high_5_ema']
            ema20 = stock['high_20_ema']

            signal = stock['macds']        # Your signal line
            macd   = stock['macd']         # The MACD that need to cross the signal line to give you a Buy/Sell signal
            listLongShort = ["No data"]    # Since you need at least two days in the for loop

            for i in range(1, len(signal)):
                # If the MACD crosses the signal line upward BUY!
                if macd[i] > signal[i] and macd[i - 1] <= signal[i - 1]:
                    listLongShort.append("BUY")
                # The other way around. SELL
                elif macd[i] < signal[i] and macd[i - 1] >= signal[i - 1]:
                    listLongShort.append("SELL")
                # Do nothing if not crossed
                else:
                    listLongShort.append("HOLD")

            stock['Advice'] = listLongShort

            # The advice column means "Buy/Sell/Hold" at the end of this day or
            #  at the beginning of the next day, since the market will be closed
            #print(stock['Advice'])

            output_notebook()

            df_limit = dfCopy.copy()
            inc = df_limit.close > df_limit.open
            dec = df_limit.open > df_limit.close

            title = 'TEST PLOTTING'
            p = figure(x_axis_type="datetime", plot_width=1000, title=title)
            p.xaxis.formatter=DatetimeTickFormatter(
                                                    hours=["%d %B %Y"],
                                                    days=["%d %B %Y"],
                                                    months=["%d %B %Y"],
                                                    years=["%d %B %Y"],
                                                )

            p.line(df_limit.datetime, df_limit.close, color='black')

            # plot macd strategy
            p.line(df_limit.datetime, 0, color='black')
            p.line(df_limit.datetime, df_limit.macd, color='blue')
            p.line(df_limit.datetime, df_limit.macds, color='orange')
            p.vbar(x=df_limit.datetime, bottom=[0 for _ in df_limit.datetime], top=df_limit.macdh, width=4, color="purple")

            # plot candlesticks
            candlestick_width = 3600 * 1000 # 1 hour in ms
            p.segment(df_limit.datetime, df_limit.high, df_limit.datetime, df_limit.low, color="black")
            p.vbar(df_limit.datetime[inc], candlestick_width, df_limit.open[inc],
                   df_limit.close[inc], fill_color="#57a52c", line_color="black")
            p.vbar(df_limit.datetime[dec], candlestick_width, df_limit.open[dec],
                   df_limit.close[dec], fill_color="#dd0000", line_color="black")

            # Plot buy and sell signals
            linecolor = []
            alpha = []
            for i, a in enumerate(df_limit.Advice):
                if (a == "BUY"):
                    alpha.append(1)
                    linecolor.append("green")
                elif (a == "SELL"):
                    alpha.append(1)
                    linecolor.append("red")
                else:
                    alpha.append(0)
                    linecolor.append("black")

            p.text(df_limit.datetime, df_limit.high + 50, text=df_limit.Advice, text_color=linecolor, text_alpha=alpha, angle=1.0)

            output_file("visualizing_trading_strategy.html", title="visualizing trading strategy")
            show(p)

    def logPrice(self, append = True):
        mode='w'
        if (append):
            mode = 'a'
        self.ema_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', mode=mode, index=False, header=not append)
