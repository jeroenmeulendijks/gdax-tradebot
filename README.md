# gdax-tradebot

Experimental GDAX (https://www.gdax.com) trading bot.

# Getting Started

These instructions allow you to get running and customise the project.

### Prerequisites

You will need a GDAX account and an API key. Create a config file (config.py) in the root directory with the following format:

```
API_KEY = ""
API_SECRET = ""
API_PASS = ""

USE_SANDBOX = 1     # 0 for gdax live environment; 1 for use the sandbox environment
TEST_MODE = 0       # 0 for actual trading against the exchange; 1 for test mode (no trading!)
USE_TEST_PRICES = 0 # 0 to get prices from gdax, 1 to use test prices

# Enable/Disable plotting the candles and indicators
# 0: disable plotting
# 1: enable plotting (Only enable it when you are debugging your algorithm)
PLOT = 1

# Configure which currencies you want to use
# Possible values for gdax 'BTC-EUR', 'ETH-EUR', 'LTC-EUR'
PRODUCT_IDS = ['BTC-EUR']

CANDLE_TIME = 60    # Seconds for accumulating in 1 candlesticks
ORDER_TIMEOUT = 15  # Seconds after which an (not filled) order is canceled automatically

# Select which indicators you want to use
# Possible values 'EMA', 'DMI', 'MACD', 'RSI'
INDICATORS = ['EMA', 'MACD']
```

The project was built and tested with Python 3.6.5. To install the required packages, run the following:

```
pip install -r requirements.txt
pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
```

To run an example set TEST_MODE = 1 and USE_TEST_PRICES = 1 and run
```
python -u example.py
```

## License

This project is licensed under the MIT License

## Acknowledgments

This project is started as a fork of https://github.com/emperorcal/gdax-tradingbot, but has been completely rewritten!