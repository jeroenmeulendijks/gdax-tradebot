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

USE_SANDBOX = 0     # 0 for gdax live environment; 1 for use the sandbox environment (Make sure to use sandbox keys!)
TEST_MODE = 1       # 0 for actual trading against the exchange; 1 for test mode (no trading!)
USE_TEST_PRICES = 1 # 0 to get prices from gdax, 1 to use test prices

# Configure which currencies you want to use
# Possible values for gdax 'BTC-EUR', 'ETH-EUR', 'LTC-EUR'
PRODUCT_IDS = ['BTC-EUR']

# Select which indicators you want to use
# Possible values 'EMA', 'DMI', 'MACD', 'RSI'
INDICATORS = ['EMA', 'MACD']

# Enable/Disable plotting the candles and indicators
# 0: disable plotting
# 1: enable plotting (Only enable it when you are debugging your algorithm)
PLOT = 1

CANDLE_TIME = 3600  # Seconds for accumulating in 1 candlestick
ORDER_TIMEOUT = 900 # Seconds after which an (not filled) order is canceled automatically

# Set the amount (%) of the balance you want to trade. 1 means everything; a value between 0 and 1 is valid
BALANCE_FOR_TRADING = 1

# Set the price offset you want to use for buying/selling. (Value between 0 and 1)
# When set to 0.02 selling will be done 2% above price of the moment of the order
# and 2% below the price of the moment of the order
TRADE_PRICE_OFFSET = 0.02

# Test variables (only used when TEST_MODE == 1)
BALANCES = {'BTC': 0.00, 'EUR': 200, 'ETH': 0.00, 'LTC': 0.00}
```

The project was built and tested with Python 3.6.5. To install the required packages, run the following:

```
pip install -r requirements.txt
# Only needed when you want to plot
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

## Disclaimer
- This bot is NOT a sure-fire profit machine. Use it AT YOUR OWN RISK.
- Crypto-currency is still an experiment, and therefore so is this bot. Meaning, both may fail at any time.
- Running a bot, and trading in general requires careful study of the risks and parameters involved. A wrong setting can cause you a major loss.
- Never leave the bot un-monitored for long periods of time. This bot doesn't know when to stop, so be prepared to stop it if too much loss occurs.
- Often times the default trade parameters will underperform vs. a buy-hold strategy, so run some simulations and find the optimal parameters for your chosen exchange/pair before going "all-in".

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.