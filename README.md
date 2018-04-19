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
API_URL = "https://api.gdax.com/" # Sandbox: https://api-public.sandbox.gdax.com/

TEST_MODE = 1       # 0 for actual trading against the exchange; 1 for test mode (no trading!)
USE_TEST_PRICES = 0 # 0 to get prices from gdax, 1 to use test prices in candles.py
```

The project was built and tested with Python 3.6.4. To install the required packages, run the following:

```
pip install -r requirements.txt
pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
```
### Customisation

To customise the project you can edit the following variables, as shown in example.py:

```
PRODUCT_IDS = ['BTC-EUR', 'ETH-EUR'] # Configure which currencies you want to use
PLOT = 1 # 0: disable plotting
         # 1: enable plotting (Only enable it when you are debugging your algorithm)
         #    Also you can only plot max 4 graphs so make sure PRODUCT_IDS doesn't contain more than 4 product id's
CANDLE_TIME = 15    # Seconds for accumulating in 1 candlesticks
ORDER_TIMEOUT = 15  # Seconds after which an (not filled) order is canceled automatically
```

To run an example set TEST_MODE = 1 and run
```
python -u example.py
```

## License

This project is licensed under the MIT License

## Acknowledgments

This project is started as a fork of https://github.com/emperorcal/gdax-tradingbot