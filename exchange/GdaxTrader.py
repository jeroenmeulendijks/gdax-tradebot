import gdax
import logging
import uuid

from config import *

logger = logging.getLogger('gdax-tradebot')

def getTrader():
    if (TEST_MODE):
        return DemoTrader()
    else:
        return GdaxTrader(api_key=API_KEY, api_secret=API_SECRET, passphrase=API_PASS)

class GdaxTrader(gdax.trader.Trader):
    if (USE_SANDBOX):
        API_URL = "https://api-public.sandbox.gdax.com"
    else:
        API_URL = "https://api.gdax.com"

    async def buy(self, product_id=None, price=None, size=None, funds=None,
                  **kwargs):
        await self.logBalance()

        return await super().buy(product_id, price, size, funds, **kwargs)

    async def sell(self, product_id=None, price=None, size=None, funds=None,
                   **kwargs):
        await self.logBalance()

        return await super().sell(product_id, price, size, funds, **kwargs)

    async def logBalance(self):
        accounts = await self.get_account()
        for account in accounts:
            if (float(account['balance']) > 0.0):
                logger.info("Currency: {} Balance: {}".format(account['currency'], account['balance']))

class DemoTrader(object):

    def __init__(self):
        # Create some test accounts with balance
        self.accounts = []
        profileId = str(uuid.uuid4())
        for currency, balance in BALANCES.items():
            account = {}
            account['id'] = str(uuid.uuid4())
            account['currency'] = currency
            account['balance'] = balance
            account['available'] = account['balance']
            account['hold'] = 0
            account['profile_id'] = profileId
            account['startBalance'] = account['balance']
            self.accounts.append(account)

    async def buy(self, product_id=None, price=None, size=None, funds=None,
                  **kwargs):
        self.updateBalance('buy', product_id, price, size)

        return self.createFilledOrderResult(size)

    async def sell(self, product_id=None, price=None, size=None, funds=None,
                   **kwargs):
        self.updateBalance('sell', product_id, price, size)

        return self.createFilledOrderResult(size)

    async def get_products(self):
        products = []
        products.append({'id': 'BTC-EUR', 'base_currency': 'BTC', 'quote_currency': 'EUR', 'base_min_size': '0.01', 'base_max_size': '10000', 'quote_increment': '0.01', 'display_name': 'BTC/EUR', 'status': 'online', 'margin_enabled': False, 'status_message': None, 'min_market_funds': None, 'max_market_funds': None, 'post_only': False, 'limit_only': False, 'cancel_only': False})
        products.append({'id': 'ETH-BTC', 'base_currency': 'ETH', 'quote_currency': 'BTC', 'base_min_size': '0.01', 'base_max_size': '1000000', 'quote_increment': '0.00001', 'display_name': 'ETH/BTC', 'status': 'online', 'margin_enabled': False, 'status_message': None, 'min_market_funds': None, 'max_market_funds': None, 'post_only': False, 'limit_only': False, 'cancel_only': False})
        products.append({'id': 'LTC-BTC', 'base_currency': 'LTC', 'quote_currency': 'BTC', 'base_min_size': '0.01', 'base_max_size': '1000000', 'quote_increment': '0.00001', 'display_name': 'LTC/BTC', 'status': 'online', 'margin_enabled': False, 'status_message': None, 'min_market_funds': None, 'max_market_funds': None, 'post_only': False, 'limit_only': False, 'cancel_only': False})
        products.append({'id': 'ETH-EUR', 'base_currency': 'ETH', 'quote_currency': 'EUR', 'base_min_size': '0.01', 'base_max_size': '1000000', 'quote_increment': '0.01', 'display_name': 'ETH/EUR', 'status': 'online', 'margin_enabled': False, 'status_message': None, 'min_market_funds': None, 'max_market_funds': None, 'post_only': False, 'limit_only': False, 'cancel_only': False})
        products.append({'id': 'LTC-EUR', 'base_currency': 'LTC', 'quote_currency': 'EUR', 'base_min_size': '0.1', 'base_max_size': '1000', 'quote_increment': '0.01', 'display_name': 'LTC/EUR', 'status': 'online', 'margin_enabled': False, 'status_message': None, 'min_market_funds': '10', 'max_market_funds': '200000', 'post_only': False, 'limit_only': False, 'cancel_only': False})

        return products

    async def get_account(self, account_id=''):
        if (account_id == ''):
            return self.accounts
        else:
            for account in self.accounts:
                if (account['id'] == account_id):
                    return account

    async def get_order(self, order_id):
        # For now not needed because order is immediately filled and this method should never be called
        raise NotImplementedError

    async def cancel_order(self, order_id):
        # For now not needed because order is immediately filled and this method should never be called
        raise NotImplementedError

    async def cancel_all(self, data=None, product_id=''):
        # For now not needed because order is immediately filled and this method should never be called
        raise NotImplementedError

    def updateBalance(self, type, product_id, price, size):
        crypto, currency = product_id.split("-")
        account = self.getAccount(currency)

        if (type == 'buy'): account['balance'] -= (size * price)
        else: account['balance'] += (size * price)
        account['available'] = account['balance']

        account = self.getAccount(crypto)
        if (type == 'buy'): account['balance'] += size
        else: account['balance'] -= size
        account['available'] = account['balance']

        for account in self.accounts:
            startBalance = account['startBalance']
            if (startBalance > 0):
                profit = ((account['balance'] - startBalance) / startBalance) * 100
            else:
                profit = "*"
            logger.info("Currency: {} Balance: {} Profit: {} % ({})".format(account['currency'],
                                                                            account['balance'],
                                                                            profit,
                                                                            startBalance))

    def getAccount(self, currency):
        for account in self.accounts:
            if (account['currency'] == currency):
                return account

    def createFilledOrderResult(self, size):
        res = {}
        res['id'] = str(uuid.uuid4())
        res['status'] = 'done'
        res['done_reason'] = 'filled'
        res['filled_size'] = size
        return res
