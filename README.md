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

TEST_MODE = 1 # 0 for actual trading against the exchange; 1 for test mode
USE_TEST_PRICES = 1 # 0 to get prices from gdax, 1 to use test prices in candles.py
```

The project was built and tested with Python 3.6.4. To install the required packages, run the following:

```
pip install -r requirements.txt
```
### Customisation

To customise the project you can edit the following variables, as shown in example.py:

```
LOOP_DURATION = 60 # Time period (in seconds)
MAX_LOOP_TIME = 8 * 60 * 60 # Max duration to run (in seconds)
QUOTE_CURRENCY = "BTC" # Cryptocurrency of choice
BASE_CURRENCY = "EUR" # Fiat currency of choice
CSV_PRICE = "price.csv" # Price CSV name
```

To run an example set TEST_MODE = 1 and run
```
python -u example.py
```

## License

This project is licensed under the MIT License

## Acknowledgments

This project is started as a fork of https://github.com/emperorcal/gdax-tradingbot